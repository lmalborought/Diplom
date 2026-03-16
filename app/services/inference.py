import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import MODEL_PATH, HF_TOKEN


class InferenceService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased",
            token=HF_TOKEN)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "DeepPavlov/rubert-base-cased",
            token=HF_TOKEN,
            num_labels=10,
        )

        state_dict = torch.load(str(MODEL_PATH), map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        self.labels = [
            "Бэкенд",
            "Фронтенд",
            "Администрирование",
            "Информационная безопасность",
            "Геймдев",
            "AI и ML",
            "Дизайн",
            "Менеджмент",
            "Маркетинг и контент",
            "Научпоп",
        ]

    def predict(self, text: str) -> str:
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        pred_id = torch.argmax(outputs.logits, dim=1).item()
        return self.labels[pred_id]
