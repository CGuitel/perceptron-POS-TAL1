# corpus:
# https://universaldependencies.org/treebanks/fr_gsd/index.html#ud-french-gs
# https://github.com/UniversalDependencies/UD_French-GSD

# bibliography: 
# https://moodle.u-paris.fr/pluginfile.php/649525/mod_resource/content/1/perceptron.pdf (training pseudo-code algorithm)
# https://www.nltk.org/_modules/nltk/tag/perceptron.html
# https://www.guru99.com/pos-tagging-chunking-nltk.html
# https://becominghuman.ai/part-of-speech-tagging-tutorial-with-the-keras-deep-learning-library-d7f93fa05537 (list of features)

import random
import time

def get_word_vector(sentence, word, index): 
	#hypothesis: word, word before, word after, pre- and suffixes with len from 1 to 3, are enough to determine POS tagging
	vector = {}

	if index == 0:
		vector["is_first"] = 1
	if index == len(sentence) -1:
		vector["is_last"] = 1
	if word[0].upper() == word[0]:
		vector["is_capitalized"] = 1
	if word.upper() == word:
		vector["is_uppercase"] = 1

	word_minus_1 = ""
	if index != 0:
		word_minus_1 = sentence[index-1]
	vector["word-1="+word_minus_1] = 1

	vector["word="+word] = 1

	word_plus_1 = ""
	if index < len(sentence) - 1:
		word_plus_1 = sentence[index+1]
	vector["word-1="+word_plus_1] = 1

	#To do : determine if "", then still a feature, or if then = 0
	prefix_1 = ""
	if len(word) > 0:
		prefix_1 = word[0:1]
	vector["prefix1="+prefix_1] = 1

	prefix_2 = ""
	if len(word) > 1:
		prefix_1 = word[0:2]
	vector["prefix2="+prefix_2] = 1

	prefix_3 = ""
	if len(word) > 2:
		prefix_3 = word[0:3]
	vector["prefix3="+prefix_3] = 1

	suffix_1 = ""
	if len(word) > 0:
		suffix_1 = word[0:1]
	vector["suffix1="+suffix_1] = 1

	suffix_2 = ""
	if len(word) > 1:
		suffix_2 = word[0:2]
	vector["suffix2="+suffix_2] = 1

	suffix_3 = ""
	if len(word) > 2:
		suffix_3 = word[0:3]
	vector["suffix3="+suffix_3] = 1
	
	#print(vector)

	return vector



def predict_tag(vector, weights, tagset):
	scores = {}
	for tag in tagset:
		scores[tag] = 0
		for feature in weights:
			if feature in vector:
				scores[tag] += weights[feature].get(tag,0) * vector[feature]
	return max(scores, key=lambda tag: (scores[tag], tag))



def add_vector_to_weights(vector, weights, tag, factor):
	for feature in vector:
		weights[feature] = weights.get(feature, {})
		weights[feature][tag] = (weights[feature]).get(tag, 0) + vector[feature]*factor



def add_weights_to_average(average, weights):
	for feature in weights:
		for tag in weights[feature]:
			average[feature] = average.get(feature, {})
			average[feature][tag] = average[feature].get(tag, 0) + weights[feature][tag]



def train(vectors_corpus, tagset, MAX_EPOCH = 1):
	
	"""création du dictionnaire train
	"""
	average = {}

	for epoch in range(0, MAX_EPOCH):
		print("epoch: "+str(epoch))
		weights = {}
		random.shuffle(vectors_corpus)
		index_word = 0
		n_words = len(vectors_corpus)
		for word in vectors_corpus:
			#print("epoch "+str(epoch)+"/"+str(MAX_EPOCH)+": "+str(index_word)+"/"+str(n_words)+" words") #TBD
			index_word += 1
			predicted_tag = predict_tag(word[0], weights, tagset)
			gold_tag = word[1]
			if predicted_tag != gold_tag:
				add_vector_to_weights(word[0], weights, predicted_tag, -1)
				add_vector_to_weights(word[0], weights, gold_tag, +1)
			add_weights_to_average(average, weights)
	#print(average) # TBD
	return average



def get_data_from_file(file = "./fr_gsd-ud-train.conllu"):
	
	"""extraction des données à partir des fichiers conllu
	   return : list de dictionnaires 
       (exemple pour une phrase : 
		[{index du mot dans la phrase : 1, mot : mot1, gold_pos : ADV}, 
         {index du mot dans la phrase 2, mot : mot2, gold_pos : DET}], etc."""
	
	data = [] # list of lists (sentences) of dictionaries (words)

	with open(file, "r") as raw_file:
		raw_content = raw_file.read()
		sentences = raw_content.split("\n\n")
		for sentence in sentences:
			sentence_data = []
			for line in sentence.split("\n"):
				if line != "" and line[0] != "#":
					tabs = line.split("\t")
					if tabs[3] != "_":
						to_append = {}
						to_append["index"] = int(tabs[0])
						to_append["word"] = tabs[1]
						to_append["gold_POS"] = tabs[3]
						sentence_data.append(to_append)
			data.append(sentence_data)
	
	return data


def get_vectors_from_data(data):
	
	"""Création des vecteurs à partir des données extraites du fichiers
	   return : list of tuples""" 
	
	# vectors: list of tuples, with (word vector, gold POS tag)
	vectors = []
	for sentence_data in data:
		sentence = []
		for word_data in sentence_data:
			sentence.append(word_data["word"])
		for word_data in sentence_data:
			word_vector = get_word_vector(sentence, word_data["word"], word_data["index"])
			to_append = (word_vector, word_data["gold_POS"])
			vectors.append(to_append)
	return vectors


if "__main__" == __name__:
	
	start_time = time.time()
	
	#train_data = get_data_from_file("./fr_gsd-ud-train.conllu")
	dev_data = get_data_from_file("./fr_gsd-ud-dev.conllu")
	
	#test_data = get_data_from_file("./fr_gsd-ud-test.conllu")

	#train_vectors = get_vectors_from_data(train_data)
	dev_vectors = get_vectors_from_data(dev_data)
	#test_vectors = get_vectors_from_data(test_data)
	

	tagset = ["ADJ","ADP","ADV","AUX","CCONJ","DET","INTJ","NOUN","NUM","PART","PRON","PROPN","PUNCT","SCONJ","SYM","VERB","X"]

	weigths = {} #donc que des 0 
	weights = train(dev_vectors, tagset) #weights[feature][tag]
	
	print(int(time.time()-start_time), " secondes")

	#To do : validation with MAX_EPOCH and dev_vectors
	#To do : evaluation with test_vectors
