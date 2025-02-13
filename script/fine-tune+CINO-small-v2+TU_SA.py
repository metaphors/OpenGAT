from transformers import XLMRobertaForSequenceClassification
from transformers import TrainingArguments
from datasets import load_dataset
from transformers import XLMRobertaTokenizer
from transformers import DataCollatorWithPadding
from evaluate import combine
from numpy import argmax
from transformers import Trainer

id2label = {0: "Negative", 1: "Positive"}
label2id = {"Negative": 0, "Positive": 1}

model = XLMRobertaForSequenceClassification.from_pretrained("data/PLM.XLM-RoBERTa.CINO-small-v2",
                                                            num_labels=2, id2label=id2label, label2id=label2id)

training_args = TrainingArguments(
    output_dir="data/Victim.XLM-RoBERTa.CINO-small-v2+TU_SA",
    eval_strategy="steps",
    save_strategy="steps",
    eval_steps=100,
    save_steps=100,
    save_safetensors=False,
    save_only_model=True,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    per_device_train_batch_size=32,
    per_device_eval_batch_size=32,
    num_train_epochs=40,
    learning_rate=5e-5,
    warmup_ratio=0.1
)

dataset = load_dataset("data/Dataset.Loader/TU_SA.py")

tokenizer = XLMRobertaTokenizer.from_pretrained("data/PLM.XLM-RoBERTa.CINO-small-v2")


def tokenize(examples):
    return tokenizer(examples["text"], max_length=512, padding="max_length", truncation=True)


tokenized_dataset = dataset.map(tokenize, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

clf_metrics = combine(["accuracy", "precision", "recall", "f1"])


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = argmax(logits, axis=-1)
    return clf_metrics.compute(predictions=predictions, references=labels)


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
