from transformers import XLMRobertaForSequenceClassification
from transformers import TrainingArguments
from datasets import load_dataset
from transformers import XLMRobertaTokenizer
from transformers import DataCollatorWithPadding
from evaluate import load
from numpy import argmax
from transformers import Trainer

id2label = {0: "Politics", 1: "Economics", 2: "Education", 3: "Tourism", 4: "Environment", 5: "Language",
            6: "Literature", 7: "Religion", 8: "Arts", 9: "Medicine", 10: "Customs", 11: "Instruments"}
label2id = {"Politics": 0, "Economics": 1, "Education": 2, "Tourism": 3, "Environment": 4, "Language": 5,
            "Literature": 6, "Religion": 7, "Arts": 8, "Medicine": 9, "Customs": 10, "Instruments": 11}

model = XLMRobertaForSequenceClassification.from_pretrained("data/PLM.XLM-RoBERTa.CINO-base-v2",
                                                            num_labels=12, id2label=id2label, label2id=label2id)

training_args = TrainingArguments(
    output_dir="data/Victim.XLM-RoBERTa.CINO-base-v2+TNCC-document",
    eval_strategy="steps",
    save_strategy="steps",
    eval_steps=100,
    save_steps=100,
    save_safetensors=False,
    save_only_model=True,
    load_best_model_at_end=True,
    metric_for_best_model="macro-f1",
    per_device_train_batch_size=32,
    per_device_eval_batch_size=32,
    num_train_epochs=40,
    learning_rate=5e-5,
    warmup_ratio=0.1
)

dataset = load_dataset("data/Dataset.Loader/TNCC-document.py")

tokenizer = XLMRobertaTokenizer.from_pretrained("data/PLM.XLM-RoBERTa.CINO-base-v2")


def tokenize(examples):
    return tokenizer(examples["text"], max_length=512, padding="max_length", truncation=True)


tokenized_dataset = dataset.map(tokenize, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

accuracy_metric = load("accuracy")
precision_metric = load("precision")
recall_metric = load("recall")
f1_metric = load("f1")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = argmax(logits, axis=-1)
    accuracy_metric_results = accuracy_metric.compute(predictions=predictions, references=labels)
    macro_precision_metric_results = precision_metric.compute(
        predictions=predictions, references=labels, average="macro")
    macro_precision_metric_results["macro-precision"] = macro_precision_metric_results.pop("precision")
    macro_recall_metric_results = recall_metric.compute(predictions=predictions, references=labels, average="macro")
    macro_recall_metric_results["macro-recall"] = macro_recall_metric_results.pop("recall")
    macro_f1_metric_results = f1_metric.compute(predictions=predictions, references=labels, average="macro")
    macro_f1_metric_results["macro-f1"] = macro_f1_metric_results.pop("f1")
    weighted_precision_metric_results = precision_metric.compute(
        predictions=predictions, references=labels, average="weighted")
    weighted_precision_metric_results["weighted-precision"] = weighted_precision_metric_results.pop("precision")
    weighted_recall_metric_results = recall_metric.compute(
        predictions=predictions, references=labels, average="weighted")
    weighted_recall_metric_results["weighted-recall"] = weighted_recall_metric_results.pop("recall")
    weighted_f1_metric_results = f1_metric.compute(predictions=predictions, references=labels, average="weighted")
    weighted_f1_metric_results["weighted-f1"] = weighted_f1_metric_results.pop("f1")
    clf_metrics_results = {**accuracy_metric_results,
                           **macro_precision_metric_results, **macro_recall_metric_results, **macro_f1_metric_results,
                           **weighted_precision_metric_results, **weighted_recall_metric_results,
                           **weighted_f1_metric_results}
    return clf_metrics_results


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"].shuffle(),
    eval_dataset=tokenized_dataset["validation"].shuffle(),
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

trainer.train()
