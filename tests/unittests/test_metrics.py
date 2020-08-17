import torch
import torch.nn


def test_metric_stats():
    from speechbrain.utils.metric_stats import MetricStats
    from speechbrain.nnet.losses import l1_loss

    def batch_l1_loss(pred, target, length):
        return l1_loss(pred, target, length, reduction="batch")

    l1_stats = MetricStats(metric=batch_l1_loss)
    l1_stats.append(
        ids=["utterance1", "utterance2"],
        predict=torch.tensor([[0.1, 0.2], [0.1, 0.2]]),
        target=torch.tensor([[0.1, 0.3], [0.2, 0.3]]),
        pred_len=torch.ones(2),
    )
    summary = l1_stats.summarize()
    assert summary["average"].isclose(torch.Tensor([0.075]))
    assert summary["min_score"].isclose(torch.Tensor([0.05]))
    assert summary["min_id"] == "utterance1"
    assert summary["max_score"].isclose(torch.Tensor([0.1]))
    assert summary["max_id"] == "utterance2"


def test_error_rate_stats():
    from speechbrain.utils.metric_stats import ErrorRateStats

    wer_stats = ErrorRateStats()
    wer_stats.append(
        ids=["utterance1", "utterance2"],
        predict=[[3, 2, 1], [2, 3]],
        target=torch.tensor([[3, 2, 0], [2, 1, 0]]),
        target_len=torch.tensor([0.67, 0.67]),
        ind2lab={1: "hello", 2: "world", 3: "the"},
    )
    summary = wer_stats.summarize()
    assert summary["WER"] == 50.0
    assert summary["insertions"] == 1
    assert summary["substitutions"] == 1
    assert summary["deletions"] == 0
    assert wer_stats.scores[0]["ref_tokens"] == ["the", "world"]
    assert wer_stats.scores[0]["hyp_tokens"] == ["the", "world", "hello"]


def test_binary_metrics():
    from speechbrain.utils.metric_stats import BinaryMetricStats

    binary_stats = BinaryMetricStats()
    binary_stats.append(
        ids=["utt1", "utt2", "utt3", "utt4", "utt5", "utt6"],
        scores=[0.1, 0.4, 0.8, 0.2, 0.3, 0.6],
        labels=[1, 0, 1, 0, 1, 0],
    )
    summary = binary_stats.summarize(threshold=0.5)
    assert summary["TP"] == 1
    assert summary["TN"] == 2
    assert summary["FP"] == 1
    assert summary["FN"] == 2

    summary = binary_stats.summarize()


def test_EER_threshold():
    from speechbrain.utils.metric_stats import eer_threshold

    positive_scores = torch.tensor([0.1, 0.2, 0.3])
    negative_scores = torch.tensor([0.4, 0.5, 0.6])
    threshold = eer_threshold(positive_scores, negative_scores)
    assert threshold > 0.3 and threshold < 0.4

    positive_scores = torch.tensor([0.4, 0.5, 0.6])
    negative_scores = torch.tensor([0.3, 0.2, 0.1])
    threshold = eer_threshold(positive_scores, negative_scores)
    assert threshold > 0.3 and threshold < 0.4

    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    input1 = torch.randn(1000, 64)
    input2 = torch.randn(1000, 64)
    positive_scores = cos(input1, input2)

    input1 = torch.randn(1000, 64)
    input2 = torch.randn(1000, 64)
    negative_scores = cos(input1, input2)

    threshold = eer_threshold(positive_scores, negative_scores)

    correct = (positive_scores > threshold).nonzero(as_tuple=False).size(0) + (
        negative_scores < threshold
    ).nonzero(as_tuple=False).size(0)

    assert correct > 950 and correct < 1050
