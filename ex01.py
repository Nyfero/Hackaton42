from NN.model_for_mnist import *
import numpy as np
from sklearn.model_selection import train_test_split
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt
import random
import os
from noise import *

use_cuda = torch.cuda.is_available()
use_cuda = False
device = torch.device("cuda" if use_cuda else "cpu")

def cut_img(img, start_height, end_height, start_width, end_width):
	return img[:, start_height:end_height, start_width:end_width]

def deplace_bottom_img(empty_img, original, deplacement):
	for row in range(empty_img.shape[1]):
		if row >= deplacement:
			empty_img[:, row, :] = original[:, row - deplacement, :]
	return empty_img

def deplace_upper_img(empty_img, original, deplacement):
	for row in range(empty_img.shape[1]):
		if row <= deplacement:
			empty_img[:, row, :] = original[:, row + deplacement, :]
	return empty_img

def deplace_right_img(empty_img, original, deplacement):
	for col in range(empty_img.shape[2]):
		if col >= deplacement:
			empty_img[:, :, col] = original[:, :, col - deplacement]
	return empty_img

def deplace_left_img(empty_img, original, deplacement):
	for col in range(empty_img.shape[2]):
		if col <= deplacement:
			empty_img[:, :, col] = original[:, :, col + deplacement]
	return empty_img


dataset_name = 'datasets2/01_mnist_cc'
X_labeled = np.load(join(dataset_name, "X_labeled.npy"))
y_labeled = np.load(join(dataset_name, "y_labeled.npy"))
X_unlabeled = np.load(join(dataset_name, "X_unlabeled.npy"))
X_val = np.load(join(dataset_name, "X_val.npy"))

# Keep only left side of image for
X_lab_left = np.zeros((X_labeled.shape[0], 1, 28, 28))
for i in range(X_labeled.shape[0]):
	X_lab_left[i] = cut_img(X_labeled[i], 0, 28, 0, 28)

X_unlab_left = np.zeros((X_unlabeled.shape[0], 1, 28, 28))
for i in range(X_unlabeled.shape[0]):
	X_unlab_left[i] = cut_img(X_unlabeled[i], 0, 28, 0, 28)

X_val_left = np.zeros((X_val.shape[0], 1, 28, 28))
for i in range(X_val.shape[0]):
	X_val_left[i] = cut_img(X_val[i], 0, 28, 0, 28)

# Check cut obtained images
#fig, axs = plt.subplots(10, 10, figsize=(50, 50))
#for i in range(10):
#	for j in range(10):
#		rd_ind = random.choice(range(X_lab_left.shape[0]))
#		axs[i, j].imshow(X_lab_left[rd_ind, 0], cmap='gray')
#		axs[i, j].axis('off')
#		axs[i, j].set_title(f"Data {rd_ind} label {y_labeled[rd_ind]}", fontsize=7)
#fig.suptitle('Labeled data example')
#plt.show()

#fig, axs = plt.subplots(10, 10, figsize=(50, 50))
#for i in range(10):
#	for j in range(10):
#		rd_ind = random.choice(range(X_unlab_left.shape[0]))
#		axs[i, j].imshow(X_unlab_left[rd_ind, 0], cmap='gray')
#		axs[i, j].axis('off')
#		axs[i, j].set_title(f"Data {rd_ind}", fontsize=7)
#fig.suptitle('Unlabeled data example')
#plt.show()

#fig, axs = plt.subplots(10, 10, figsize=(50, 50))
#for i in range(10):
#	for j in range(10):
#		rd_ind = random.choice(range(X_val_left.shape[0]))
#		axs[i, j].imshow(X_val_left[rd_ind, 0], cmap='gray', )
#		axs[i, j].axis('off')
#		axs[i, j].set_title(f"Data {rd_ind}", fontsize=7)
#fig.suptitle('Val data example')
#plt.show()

# Creation of new data from train set
#X_bottom = np.zeros((X_lab_left.shape[0], 1, 28, 28))
#for i in range(X_lab_left.shape[0]):
#	X_bottom[i] = deplace_bottom_img(X_bottom[i], X_lab_left[i], 7)

#X_upper = np.zeros((X_lab_left.shape[0], 1, 28, 28))
#for i in range(X_lab_left.shape[0]):
#	X_upper[i] = deplace_bottom_img(X_upper[i], X_lab_left[i], 7)

#X_left = np.zeros((X_lab_left.shape[0], 1, 28, 28))
#for i in range(X_lab_left.shape[0]):
#	X_left[i] = deplace_left_img(X_left[i], X_lab_left[i], 7)

#X_right = np.zeros((X_lab_left.shape[0], 1, 28, 28))
#for i in range(X_lab_left.shape[0]):
#	X_right[i] = deplace_right_img(X_right[i], X_lab_left[i], 7)

#X_noise, y_noise = generate_random_noise(X_lab_left, y_labeled)

# Split data
x_train, x_test, y_train, y_test = train_test_split(X_lab_left, y_labeled)

# Add new data to pure training set
#x_train = np.concatenate((x_train, X_bottom[:250], X_upper[250:500], X_left[500:750], X_right[750:1000], X_noise), axis=0)
#y_train = np.concatenate((y_train, y_labeled[:250], y_labeled[250:500], y_labeled[500:750], y_labeled[750:1000], y_noise), axis=0)

x_train = torch.from_numpy(x_train).to(device).float()
y_train = torch.from_numpy(y_train).to(device)
x_test = torch.from_numpy(x_test).to(device).float()
y_test = torch.from_numpy(y_test).to(device)

# Create model for 2 classes
model = MNIST_model()
train(model, x_train, y_train, x_test, y_test, epochs=25)

# Predict on val and unlabeled data and save
try:
	os.mkdir('./ex01_results')
except:
	pass

x_unlabeled = torch.from_numpy(X_unlab_left).to(device).float()
y_unlabeled = model.forward(x_unlabeled)
y_unlabeled_numpy = y_unlabeled.detach().numpy()
y_unlabeled_numpy = np.argmax(y_unlabeled_numpy, axis=1)
df = pd.DataFrame(y_unlabeled_numpy)
df.to_csv('./ex01_results/y_unlabeled.csv', index=False, header=False)

fig, axs = plt.subplots(10, 10, figsize=(50, 50))
for i in range(10):
	for j in range(10):
		rd_ind = random.choice(range(X_val_left.shape[0]))
		axs[i, j].imshow(X_val[rd_ind, 0], cmap='gray', )
		axs[i, j].axis('off')
		axs[i, j].set_title(f"Data {rd_ind}, label {y_unlabeled_numpy[rd_ind]}", fontsize=7, color='red')
fig.suptitle('Unlabeled data example')
plt.show()

x_val = torch.from_numpy(X_val_left).to(device).float()
y_val = model.forward(x_val)
y_val_numpy = y_val.detach().numpy()
y_val_numpy = np.argmax(y_val_numpy, axis=1)
df = pd.DataFrame(y_val_numpy)
df.to_csv('./ex01_results/y_val.csv', index=False, header=False)

fig, axs = plt.subplots(10, 10, figsize=(50, 50))
for i in range(10):
	for j in range(10):
		rd_ind = random.choice(range(X_val_left.shape[0]))
		axs[i, j].imshow(X_val[rd_ind, 0], cmap='gray', )
		axs[i, j].axis('off')
		axs[i, j].set_title(f"Data {rd_ind}, label {y_val_numpy[rd_ind]}", fontsize=7, color='red')
fig.suptitle('Val data example')
plt.show()
