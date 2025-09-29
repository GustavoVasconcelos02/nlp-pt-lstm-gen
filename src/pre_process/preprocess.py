import json
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split
import pickle
import numpy as np

# Caminho do corpus gerado pelo webscraping
CORPUS_FILE = "corpus.txt"

# Parâmetros
OOV_TOKEN = "<OOV>"
TEST_SIZE = 0.2
VAL_SIZE = 0.5  # metade do test_size será validação
NUM_WORDS = None  # None para usar todo vocabulário, ou limite de palavras

# 1 Carrega e junta os textos
corpus_texts = []

with open(CORPUS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        texto = " ".join([data["titulo"]] + data["ingredientes"] + data["preparo"])
        corpus_texts.append(texto)

print(f"Total de receitas no corpus: {len(corpus_texts)}")

# 22 Tokenização
tokenizer = Tokenizer(num_words=NUM_WORDS, oov_token=OOV_TOKEN)
tokenizer.fit_on_texts(corpus_texts)

# Converte texto para sequências de inteiros
sequences = tokenizer.texts_to_sequences(corpus_texts)

word_index = tokenizer.word_index
print(f"Tamanho do vocabulário: {len(word_index)}")

# 3️ Divisão em treino / validação / teste
train_seq, temp_seq = train_test_split(sequences, test_size=TEST_SIZE, random_state=42)
val_seq, test_seq = train_test_split(temp_seq, test_size=VAL_SIZE, random_state=42)

print(f"Treino: {len(train_seq)} receitas")
print(f"Validação: {len(val_seq)} receitas")
print(f"Teste: {len(test_seq)} receitas")

# 4️ Salvar os objetos para uso posterior
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

np.save("train_seq.npy", np.array(train_seq, dtype=object))
np.save("val_seq.npy", np.array(val_seq, dtype=object))
np.save("test_seq.npy", np.array(test_seq, dtype=object))

print("✅ Pré-processamento concluído. Objetos salvos: tokenizer.pkl, train_seq.npy, val_seq.npy, test_seq.npy")
