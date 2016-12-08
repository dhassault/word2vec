# Document Similarity using Latent Semantic Analysis
========

What is it?
-----------
Find document similarity by converting documents in to Latent Semantic vectors and finding the cosine similarity of those vectors. More on [LSA](https://en.wikipedia.org/wiki/Latent_semantic_analysis)

This scipt is using the similarity server. All temporary files related to a realm are stored in ./tmp/realm_id.

First, you need to train [-t] with a corpus (ie. several documents, the more is better). Then the script indexing all documents.
After that, you can ask the similarities [-s] between a card and all indexed documents.

If you trained the program on a lot of documents (~1500 documents), you can just update the index [-i] without training.

You can delete all files created by this program [-c] if needed.

Requirements
------------
python==2.7.X
scipy==0.16.1
numpy==1.11.0
gensim==0.12.3
simserver==0.1.4

Installation :
--------------------------

installation.sh


Execution : python script
-------------------------
Master folder: 
|
 ---------dataset/
|
 ----------models/
|
 ----------similarityFinder/
|
 ----------tmp/

Training and indexing all documents for a realm:
python2.7 similarityFinder/similarityfinder.py -t realm_id

Indexing all documents without training for a realm:
python2.7 similarityFinder/similarityfinder.py -i realm_id

Create a similarities json file for  given card:
python2.7 similarityFinder/similarityfinder.py -s realm_id/card_id

A file is stored in ./__MODELS__/realm_id/card_id.json

Remove all files for a given realmid
python2.7 similarityFinder/similarityfinder.py -c realm_id


Exemples
------------------

First, train:
>> python2.7 similarityFinder/similarityfinder.py -t r_a0e5d4cc-30d9-40e1-ab9c-267f45af6469

Then ask for the similarites for de card c_1a42f70b-2687-4558-9c62-5ea094627b20 
in the realm r_a0e5d4cc-30d9-40e1-ab9c-267f45af6469:
>> python2.7 similarityFinder/similarityfinder.py -s r_a0e5d4cc-30d9-40e1-ab9c-267f45af6469/c_1a42f70b-2687-4558-9c62-5ea094627b20

The result is stored ./models/r_a0e5d4cc-30d9-40e1-ab9c-267f45af6469/similarities/c_1a42f70b-2687-4558-9c62-5ea094627b20.json





