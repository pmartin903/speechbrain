#!/usr/bin/python
import os
import torch
import speechbrain as sb

current_dir = os.path.dirname(os.path.abspath(__file__))
params_file = os.path.join(current_dir, "params.yaml")
with open(params_file) as fin:
    params = sb.yaml.load_extended_yaml(fin)

sb.core.create_experiment_directory(
    experiment_directory=params.output_folder, params_to_save=params_file,
)


class SpkIdBrain(sb.core.Brain):
    def forward(self, x, init_params=False):
        id, wavs, lens = x
        feats = params.compute_features(wavs, init_params)
        feats = params.mean_var_norm(feats, lens)

        x = params.linear1(feats, init_params)
        x = params.activation(x)
        x = params.linear2(x, init_params)
        x = torch.mean(x, dim=1, keepdim=True)
        outputs = params.softmax(x)

        return outputs, lens

    def compute_objectives(self, predictions, targets, train=True):
        predictions, lens = predictions
        uttid, spkid, _ = targets
        loss = params.compute_cost(predictions, spkid, lens)

        if not train:
            stats = {"error": params.compute_error(predictions, spkid, lens)}
            return loss, stats

        return loss

    def summarize(self, stats, test=False):
        summary = {"loss": float(sum(stats["loss"]) / len(stats["loss"]))}

        if "error" in stats:
            summary["error"] = float(sum(stats["error"]) / len(stats["error"]))

        return summary

    def on_epoch_end(self, epoch, train_stats, valid_stats):
        print("Epoch %d complete" % epoch)
        print("Train loss: %.2f" % torch.Tensor(train_stats["loss"]).mean())
        print("Valid loss: %.2f" % torch.Tensor(valid_stats["loss"]).mean())
        print("Valid error: %.2f" % torch.Tensor(valid_stats["error"]).mean())


train_set = params.train_loader()
spk_id_brain = SpkIdBrain(
    modules=[params.linear1, params.linear2],
    optimizer=params.optimizer,
    first_input=next(iter(train_set[0])),
)
spk_id_brain.fit(range(params.N_epochs), train_set, params.valid_loader())
test_stats = spk_id_brain.evaluate(params.test_loader())
print("Test error: %.2f" % torch.Tensor(test_stats["error"]).mean())
