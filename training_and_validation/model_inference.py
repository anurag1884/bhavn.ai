import re
import torch
import torch.nn.functional as F
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Load your fine-tuned model and tokenizer
model_path = './bhavnai-model'
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path, attn_implementation="eager")

# Define your label mapping (index to label)
labels = ['Angry 😠', 'Sad 😢', 'Neutral 😐', 'Happy 😊']

# Input text
input_text = 'graahaka sahaayataa kitnii bekaara hai yaahaa!'

processed_text = transliterate(input_text, sanscript.ITRANS, sanscript.DEVANAGARI)

# Tokenize input
inputs = tokenizer(processed_text, return_tensors='pt', truncation=True, padding=True)

# Predict
with torch.no_grad():
    outputs = model(**inputs, output_attentions=True)
    probs = F.softmax(outputs.logits, dim=-1)
    attentions = outputs.attentions

    # Calculate the average attention across all layers and heads
    attentions_avg = torch.mean(attentions[-1], dim=(1, 2))  # Using the last layer for simplicity

    # Map the attention scores to token positions
    attention_scores = attentions_avg.squeeze().detach().cpu().numpy()

    # Get token ids and convert them back to text
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'].squeeze().cpu().numpy())

    # Extract keywords from the processed text based on attention values of tokens
    keywords = {kw: 0 for kw in re.findall('[।.,?!:;"\'\\(\\)\\-]|[^।.,?!:;"\'\\(\\)\\-\\s]+', processed_text) if len(kw) != 0}
    for t, a in zip(tokens, attention_scores):
        for kw in keywords.keys():
            if t.lstrip('▁') in kw:
                keywords[kw] += a
                break
    if len(keywords) != 0:
        keywords = [kw for kw, _ in sorted(keywords.items(), key=lambda item: item[1], reverse=True)]

predicted_output = {
    'text': processed_text,
    'sentiment': labels[probs.argmax().item()],
    'confidence': probs.max().item(),
    'keywords': keywords[:5] if keywords else [],
}

print(f'Predicted output: {predicted_output}')