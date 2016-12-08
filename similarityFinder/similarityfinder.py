#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import argparse
import ConfigParser
import json
import logging
import os
import shutil
from gensim import utils
from simserver import SessionServer


class DirIter(object):

    def __init__(self):
        self.file_dat = {}

    def parse_card(self, path):
        """Extract the card uid and the content of a card (used in iter)
            inputs: the path of the file to parse
            outputs: dic to put in file_dat after """
        try:
            card_json = json.loads(open(path).read())
            dic = {card_json['guid']: {'content': card_json['content'], 'cardGUID': card_json['guid']}}
        except (IOError, ValueError):
            card_json = {}
            dic = {}
            pass
        return dic

    def parse_file(self, path):
        """Extract the file id and the content from de .json (id) and .txt (text)
            inputs: the path of the file to parse
            outputs: dic to put in file_dat after """
        try:
            file_json = json.loads(open(path).read())
            file_txt_name = path.replace(".json", ".txt") # to extract from .txt the content
            file_txt = open(file_txt_name).read()
            dic = {file_json['ID']: {'content':file_txt, 'cardGUID': file_json['cardGUID']}}
        except (IOError, ValueError):
            file_json = {}
            file_txt = {}
            dic = {}
            pass
        return dic

    def iter_desk(self, realm_id, ideadesk_id):
        """Looks for cards and files directories to get id and content for a realm_id
            inputs: self.file_dat (empty)
                    realm_id given as argument
            outputs: fill self.file_dat"""
        deck_dict = {}
        meta_dict = {}
        corpus = []
        json_results = []
        realm_path = __REALMSDIR__+realm_id+'/'+ideadesk_id
        if not os.path.exists(__RESULTS__+realm_id):
            try:
                os.mkdir(__RESULTS__+realm_id)
            except OSError:
                pass
        for dirs in os.listdir(realm_path):
            if dirs == 'cards':
                card_path = realm_path + '/' + dirs
                for cards in os.listdir(card_path):
                    if cards.endswith('.json'):
                        card_dict = self.parse_card(card_path + '/' + cards)
                        self.file_dat = dict(list(card_dict.items()) + list(self.file_dat.items()))
                        for key, value in card_dict.items():
                            json_results_tmp = { 'id': cards.split('.')[0], 'IdeadDeskID': ideadesk_id, 'cardGUID': value['cardGUID']}  # we want to map id<>IdeadDeskID
                            json_results.append(json_results_tmp) # we want to map id<>IdeadDeskID
            if dirs == 'files':
                file_path = realm_path + '/' + dirs
                for files in os.listdir(file_path):
                    if files.endswith('.json'):
                        file_dict = self.parse_file(file_path + '/' + files)
                        self.file_dat = dict(list(file_dict.items()) + list(self.file_dat.items()))
                        for key, value in file_dict.items():
                            json_results_tmp = { 'id': files.split('.')[0], 'IdeadDeskID': ideadesk_id, 'cardGUID': value['cardGUID']} # we want to map id<>IdeadDeskID
                            json_results.append(json_results_tmp) # we want to map id<>IdeadDeskID

            out_file = open(__RESULTS__+'/'+realm_id+'/'+realm_id+".json","w") # we want to map id<>IdeadDeskID
            json.dump(json_results,out_file, indent=4)
            out_file.close()

    def iter_realm(self, realm_id):
        """Looks for cards and files directories to get id and content for a realm_id
            inputs: self.file_dat (empty)
                    realm_id given as argument
            outputs: fill self.file_dat"""
        deck_dict = {}
        meta_dict = {}

        for realm in os.listdir(__REALMSDIR__):
            corpus = []
            json_results = []
            if realm.startswith('r_'):
                realm_path = __REALMSDIR__+realm_id
                if not os.path.exists(__RESULTS__+realm_id):
                    try:
                        os.mkdir(__RESULTS__+realm_id)
                    except OSError:
                        pass
                for ideaDeskId in os.listdir(realm_path):
                    if ideaDeskId.startswith('i_'):
                        if not os.path.exists(__RESULTS__+realm_id+'/'+ideaDeskId):
                            try:
                                os.mkdir(__RESULTS__+realm_id+'/'+ideaDeskId)
                            except OSError:
                                pass
                        idi_path = realm_path + '/' + ideaDeskId
                        ideadesk_id = ideaDeskId # we want to map id<>IdeadDeskID
                        for dirs in os.listdir(idi_path):
                            if dirs == 'cards':
                                card_path = idi_path + '/' + dirs
                                for cards in os.listdir(card_path):
                                    if cards.endswith('.json'):
                                        json_results_tmp = {}
                                        card_dict = self.parse_card(card_path + '/' + cards)
                                        self.file_dat = dict(list(card_dict.items()) + list(self.file_dat.items()))
                                        json_results_tmp = { 'id': cards.split('.')[0], 'IdeadDeskID': ideadesk_id}  # we want to map id<>IdeadDeskID
                                        json_results.append(json_results_tmp) # we want to map id<>IdeadDeskID
                            if dirs == 'files':
                                file_path = idi_path + '/' + dirs
                                for files in os.listdir(file_path):
                                    if files.endswith('.json'):
                                        file_dict = self.parse_file(file_path + '/' + files)
                                        self.file_dat = dict(list(file_dict.items()) + list(self.file_dat.items()))
                                        json_results_tmp = { 'id': files.split('.')[0], 'IdeadDeskID': ideadesk_id} # we want to map id<>IdeadDeskID
                                        json_results.append(json_results_tmp) # we want to map id<>IdeadDeskID

            out_file = open(__RESULTS__+'/'+realm_id+'/'+realm_id+".json","w") # we want to map id<>IdeadDeskID
            json.dump(json_results,out_file, indent=4)
            out_file.close()


    def merge_dicts(self, *dict_args):
        """Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts."""
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)

        return result

    def train_index(self, realm_id):
        """create a semantic model of all documents in a given realm
            inputs: self.file_dat from iter funtion
                    realm_id given as argument
            outputs: files in ./tmp/realm_id/"""
        # we put self.file_dat given by iter into the corpus
        corpus = []

        for key, value in self.file_dat.items():
            corpus_iter = {'id':str(key), 'tokens':utils.simple_preprocess(str(value))}
            corpus.append(corpus_iter)

        # for safety, we delete all previous tmp file of the realm server
        server = SessionServer(__TMP__+realm_id+'/') # need writting/reading rights
        server.drop_index(False) # remove the previous server tmp created (False=remove train+index)
        ###################################################################

        # now we train the lsi model with our corpus
        server.train(corpus, method='lsi')
        server.index(corpus)
        server.optimize() # Precompute top similarities for all indexed documents.
                          # This speeds up `find_similar` queries by id

    def index_only(self, realm_id):
        """index all documents in the realm in case of new document(s).
            inputs: self.file_dat from iter funtion
                    realm_id given as argument
            outputs: files in ./tmp/realm_id/"""

        corpus = []
        for key, value in self.file_dat.items():
            corpus_iter = {'id':str(key), 'tokens':utils.simple_preprocess(str(value))}
            corpus.append(corpus_iter)
        server = SessionServer(__TMP__+realm_id+'/') # needs writting/reading rights
        server.drop_index() # removing previous index (but keep the training)
        server.index(corpus)
        server.optimize() # Precompute top similarities for all indexed documents.
                          # This speeds up `find_similar` queries by id


    def similarities(self, realm_id, uid, __SIMRATE__, __SHOWFILE__):
        """test similarities of a given document in the whole corpus and put the results in a json file
            inputs: self.file_dat from iter funtion
                    realm_id given as argument
                    uid of the object we want similarities
            outputs: a file in __RESULTS__/realm_id/uid.json"""

        server = SessionServer(__TMP__+realm_id+'/') # needs writting/reading rights
        id_ideaDeskID = json.loads(open(__RESULTS__+'/'+realm_id+'/'+realm_id+".json").read())
        # creation of the json similarities file:
        json_results_tmp = {}
        json_results = {}
        json_file_after = {}
        if uid.startswith('c_'):
            for i in server.find_similar(uid, min_score=float(__SIMRATE__), max_results=int(__SHOWFILE__)):
                if i[0] != uid: # we don't want the similarities with himself (~1.0)
                    try:
                        for k, j in enumerate(id_ideaDeskID):
                            if j['id'] == i[0]:
                                json_results_tmp = {uid+'.'+i[0]: {'id': i[0], 'realmID': realm_id, 'simIndex': i[1], 'IdeadDeskID': j['IdeadDeskID'], 'source': uid}}
                                json_results = self.merge_dicts(json_results_tmp, json_results)
                    except OSError:
                        pass
                if os.path.exists(__RESULTS__+realm_id+'/'):
                    out_file = open(__RESULTS__+'/'+realm_id+'/'+uid+".json","w")
                    json.dump(json_results,out_file, indent=4)
                    out_file.close()
                else:
                    os.mkdir(__RESULTS__+'/'+realm_id+'/')
                    out_file = open(__RESULTS__+'/'+realm_id+'/'+uid+".json","w")
                    json.dump(json_results,out_file, indent=4)
                    out_file.close()

        elif uid.startswith('f_'):
            for i in server.find_similar(uid, min_score=float(__SIMRATE__), max_results=int(__SHOWFILE__)):
                if i[0] != uid: # we don't want the similarities with himself (~1.0)
                    try:
                        for k, j in enumerate(id_ideaDeskID):
                            if j['id'] == i[0]:
                                json_results_tmp = {uid+'.'+i[0]: {'id': i[0], 'realmID': realm_id, 'simIndex': round(i[1],3), 'IdeadDeskID': j['IdeadDeskID'], 'source': uid}}
                                # i[0]+'.'+uid to have a unique id for each entries
                                json_results = self.merge_dicts(json_results_tmp, json_results)

                    except OSError:
                        pass
                elif i[0] == uid: #we want the cardguid of the file
                    for k, j in enumerate(id_ideaDeskID):
                        if j['id'] == i[0]:
                            cardGUID = j['cardGUID']
                            print(cardGUID)

            if os.path.exists(__RESULTS__+realm_id+'/'):
                try:
                    if os.path.exists(__RESULTS__+realm_id+'/'+cardGUID+".json"): #if the file exists
                        json_file_before = json.loads(open(__RESULTS__+realm_id+'/'+cardGUID+".json").read())
                        json_file_after = self.merge_dicts(json_file_before, json_results)
                    else:
                        json_file_after = json_results

                    out_file = open(__RESULTS__+realm_id+'/'+cardGUID+".json","w")
                    json.dump(json_file_after,out_file, indent=4)
                    out_file.close()
                except (IOError, ValueError):
                    pass
            else:
                try:
                    os.mkdir(__RESULTS__+'/'+realm_id+'/')
                    if os.path.exists(__RESULTS__+realm_id+'/'+cardGUID+".json"): #if the file exists
                        json_file_before = json.loads(open(__RESULTS__+realm_id+'/'+cardGUID+".json").read())
                        json_file_after = self.merge_dicts(json_file_before, json_results)
                    else:
                        json_file_after = json_results

                    out_file = open(__RESULTS__+realm_id+'/'+cardGUID+".json","w")
                    json.dump(json_file_after,out_file, indent=4)
                    out_file.close()
                except (IOError, ValueError):
                    pass

    def clear(self,realm_id):
        """remove the files created by this program for a given realm_id
            inputs: realm_id given as argument
            outputs:
        """
        shutil.rmtree(__RESULTS__+realm_id)
        shutil.rmtree(__TMP__+realm_id)



if __name__ == '__main__':
    print("Process PID:"+str(os.getpid()))
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Latent Semantic Implementation for finding similar documents - server version.')
    parser.add_argument('-t', '--train', help='Update the corpus, train and index all documents. This command needs a realm_id.', required=False)
    parser.add_argument('-i', '--index', help='Index a new document. This command needs a realm_id.', required=False)
    parser.add_argument('-s', '--similarities', help='Test the similarities of a given document. This command needs the uid of the card.', required=False)
    parser.add_argument('-c', '--clear', help='Remove all files created by this program for a given realmID.', required=False)
    args = vars(parser.parse_args())

    # we get the paths from the config file in python 2.7
    # see ./similarityFinder/config/paths.cfg for modifications
    paths = ConfigParser.ConfigParser()
    paths.read('./similarityFinder/config/paths.cfg')
    __TMP__ = paths.get('paths', '__TMP__') #tmp files of the similarity server
    __REALMSDIR__ = paths.get('paths', '__REALMSDIR__')
    __RESULTS__ = paths.get('paths', '__RESULTS__')
    __SHOWFILE__ = paths.get('paths', '__SHOWFILE__') #number of similar files to show
    __SIMRATE__ = paths.get('paths', '__SIMRATE__') #minimum score of similarities to show
    #####################################################

    it = DirIter()

    if args['train']:
        realm_id = args['train']
        if '/' in args['train']:
            realm_id = args['train'].split('/')[0]
            ideadesk_id = args['train'].split('/')[1]
            it.iter_desk(realm_id, ideadesk_id)
            it.train_index(realm_id)
        else:
            realm_id = args['train']
            it.iter_realm(realm_id)
            it.train_index(realm_id)

    if args['index']:
        realm_id = args['index']
        if '/' in args['index']:
            realm_id = args['index'].split('/')[0]
            ideadesk_id = args['index'].split('/')[1]
            it.iter_desk(realm_id, ideadesk_id)
            it.index_only(realm_id)
        else:
            realm_id = args['index']
            it.iter_realm(realm_id)
            it.index_only(realm_id)

    if args['similarities']:
        uuid = args['similarities']
        if '/' in args['similarities']:
            realm_id = args['similarities'].split('/')[0]
            uid = args['similarities'].split('/')[1]
            try:
                it.similarities(realm_id, uid, __SIMRATE__, __SHOWFILE__)
            except (IOError, ValueError):
                pass

    if args['clear']:
        realm_id = args['clear']
        try:
            it.clear(realm_id)
        except (IOError, ValueError):
            pass
