from sklearn.metrics import f1_score
import numpy as np
import pandas as pd
import math
from collections import defaultdict



def get_acc(preds, labels, num_labels,bounds):
	"""
	Calculates the accuracy for a batch of predictions with bounds.
	Args:
		preds:
		labels:
		num_labels:
		bounds:

	Returns:

	"""
	pred_convert = []
	for i in preds:
		temp_label = num_labels-1
		for b in range(len(bounds)-1, -1, -1):
			if i < bounds[b]:
				temp_label = round(b)
		pred_convert.append(temp_label)
	return np.sum(np.array(pred_convert) == labels) / len(preds)

def flat_accuracy(preds,
				  labels,
				  num_labels,
				  normalized=True,
				  bounds=None):
	"""
	Calculates the accuracy for a batch of predictions.
	Args:
		preds: list of predictions
		labels: list of labels
		num_labels: number of labels
		normalized: flag if the predictions are normalized
		bounds: bounds for the normalized predictions

	Returns:
		accuracy

	"""
	preds = preds.flatten()
	labels = labels.flatten()
	if bounds:
		pred_flat = np.array([round(i * (num_labels - 1)) for i in preds])
		labels_flat = np.array([round(i * (num_labels - 1)) for i in labels])
		pred_flat = np.array([max(min(i, num_labels - 1), 0) for i in pred_flat])
		acc = get_acc(pred_flat, labels_flat, num_labels,bounds)
	else:
		pred_flat = np.array([round(i* (num_labels - 1)) for i in preds])
		labels_flat = np.array([round(i* (num_labels - 1)) for i in labels])
		pred_flat = np.array([max(min(i, num_labels - 1), 0) for i in pred_flat])
		#pred_flat = np.array([max(min(i, num_labels - 1), 0) for i in pred_flat])
		acc=np.sum(pred_flat == labels_flat) / len(labels_flat)
	#print(acc)
	return acc

def flat_accuracy_rationale(preds, labels, classification_labels, lens, axis_=2):
	preds_li = np.argmax(preds, axis=axis_)
	all_acc = []
	for idx, elem in enumerate(preds_li):
		curr_pred = preds_li[idx]
		curr_pred = curr_pred[1:]
		curr_pred = curr_pred[:lens[idx]]

		curr_label = labels[idx]
		curr_label = curr_label[1:]
		curr_label = curr_label[:lens[idx]]

		curr_acc = np.sum(np.asarray(curr_label) == np.asarray(curr_pred)) / len(curr_label)

		all_acc.append(curr_acc)
	return np.mean(all_acc)


def get_f1(preds, labels, bounds, num_labels, mode='macro'):
	pred_convert = []
	for i in preds:
		temp_label = num_labels - 1
		for b in range(len(bounds) - 1, -1, -1):
			if i < bounds[b]:
				temp_label = b
		pred_convert.append(temp_label)
	#labels = [round(i * (num_labels - 1)) for i in labels]
	return f1_score(labels, pred_convert, average=mode)

def compute_f1(preds, labels, num_labels, normalized=True, bounds=None):
	preds = preds.flatten()
	labels = labels.flatten()

	pred_flat = np.array([round(i* (num_labels - 1)) for i in preds])
	labels_flat = np.array([round(i* (num_labels - 1)) for i in labels])
	pred_flat = np.array([max(min(i, num_labels - 1), 0) for i in pred_flat])

	if bounds:
		pos_f1 = get_f1(pred_flat, labels_flat, bounds, num_labels, mode='weighted')
		micro_f1 = get_f1(pred_flat, labels_flat, bounds, num_labels, mode='micro')
		macro_f1 = get_f1(pred_flat, labels_flat, bounds, num_labels, mode='macro')
	else:
		pos_f1 = f1_score(pred_flat, labels_flat, average='weighted')
		micro_f1 = f1_score(pred_flat, labels_flat, average='micro')
		macro_f1 = f1_score(pred_flat, labels_flat, average='macro')

	return pos_f1, micro_f1, macro_f1
def compute_f1_rationale(preds, labels, classification_labels, lens, axis_=2):
	preds_li = np.argmax(preds, axis=axis_)

	all_f1 = []

	all_labels = []
	all_f1 = []

	for idx, elem in enumerate(preds_li):

		curr_pred = preds_li[idx]
		curr_pred = curr_pred[1:]
		curr_pred = curr_pred[:lens[idx]]

		curr_label = labels[idx]
		curr_label = curr_label[1:]
		curr_label = curr_label[:lens[idx]]

		macro_f1 = f1_score(curr_pred, curr_label)

		all_f1.append(macro_f1)

	return np.mean(all_f1)

def _f1(_p, _r):
	if _p == 0 or _r == 0:
		return 0
	return 2 * _p * _r / (_p + _r)

def iou_f1(preds, labels, classification_labels, lens, axis_=2, threshold = 0.5):
	preds_li = np.argmax(preds, axis=axis_).tolist()

	all_pred_spans = []
	all_label_spans = []

	all_f1_vals = []

	for idx, elem in enumerate(preds_li):
		curr_pred = preds_li[idx]

		curr_pred = curr_pred[1:]
		curr_pred = curr_pred[:lens[idx]]

		pred_start_idx = -1
		pred_end_idx = -1

		pred_spans = []

		for inner_idx, inner_elem in enumerate(curr_pred):
			
			if inner_elem == 1:
				if pred_start_idx == -1:
					pred_start_idx = inner_idx
				
				else:
					continue 
			
			elif inner_elem == 0:
				if pred_start_idx == -1:
					continue
				else:
					pred_end_idx = inner_idx

					pred_spans.append((pred_start_idx, pred_end_idx))

					pred_start_idx = -1
					pred_end_idx = -1
		
		if pred_start_idx != -1:
			pred_end_idx = inner_idx

			pred_spans.append((pred_start_idx, pred_end_idx))


		# Labels

		curr_label = labels[idx]

		curr_label = curr_label[1:]
		curr_label = curr_label[:lens[idx]]
		
		label_start_idx = -1
		label_end_idx = -1

		label_spans = []

		for inner_idx, inner_elem in enumerate(curr_label):
			
			if inner_elem == 1:
				if label_start_idx == -1:
					label_start_idx = inner_idx
				
				else:
					continue 
			
			elif inner_elem == 0:
				if label_start_idx == -1:
					continue
				else:
					label_end_idx = inner_idx

					label_spans.append((label_start_idx, label_end_idx))

					label_start_idx = -1
					label_end_idx = -1
		
		if label_start_idx != -1:
			label_end_idx = inner_idx

			label_spans.append((label_start_idx, label_end_idx))
		
		ious = defaultdict(dict)
		for p in pred_spans:
			best_iou = 0.0
			for t in label_spans:
				num = len(set(range(p[0], p[1])) & set(range(t[0], t[1])))
				denom = len(set(range(p[0], p[1])) | set(range(t[0], t[1])))
				iou = 0 if denom == 0 else num / denom

				if iou > best_iou:
					best_iou = iou
			ious[idx][p] = best_iou

		threshold_tps = dict()

		for k, vs in ious.items():
			threshold_tps[k] = sum(int(x >= threshold) for x in vs.values())

		micro_r = sum(threshold_tps.values()) / len(label_spans) if len(label_spans) > 0 else 0
		micro_p = sum(threshold_tps.values()) / len(pred_spans) if len(pred_spans) > 0 else 0
		micro_f1 = _f1(micro_r, micro_p)
		all_f1_vals.append(micro_f1)

	return np.mean(all_f1_vals)
