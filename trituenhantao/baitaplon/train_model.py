import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import json

# ==============================
# CẤU HÌNH
# ==============================

IMG_SIZE = (128, 128)
BATCH_SIZE = 8
EPOCHS = 10
DATASET_PATH = "static"

# ==============================
# DATA AUGMENTATION
# ==============================

train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True
)

# ==============================
# TRAIN DATA
# ==============================

train_gen = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="training"
)

# ==============================
# VALIDATION DATA
# ==============================

val_gen = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="validation"
)

# ==============================
# IN THỨ TỰ CLASS
# ==============================

print("Class indices:", train_gen.class_indices)

# Lưu class ra file
with open("labels.txt", "w", encoding="utf-8") as f:
    for label in train_gen.class_indices:
        f.write(label + "\n")

# ==============================
# CNN MODEL
# ==============================

model = Sequential([

    Conv2D(32, (3,3), activation="relu", input_shape=(128,128,3)),
    MaxPooling2D(),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(),

    Conv2D(128, (3,3), activation="relu"),
    MaxPooling2D(),

    Flatten(),

    Dense(128, activation="relu"),
    Dropout(0.5),

    Dense(train_gen.num_classes, activation="softmax")
])

# ==============================
# COMPILE MODEL
# ==============================

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ==============================
# TRAIN MODEL
# ==============================

history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS
)

# ==============================
# LƯU MODEL
# ==============================

model.save("flower_model.keras")

print("✅ Train xong và đã lưu model!")

# ==============================
# LƯU HISTORY TRAIN
# ==============================

with open("training_history.json", "w") as f:
    json.dump(history.history, f)

print("✅ Đã lưu lịch sử train")