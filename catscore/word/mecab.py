import MeCab
from dataclasses import dataclass
from typing import List
from concurrent import futures
import time

@dataclass(frozen=True)
class MecabResult:
    word: str
    word_type: str
    word_kana: str

class CatsMeCab:
    """[Mecab wrapper calss]
    """
    def __init__(self, dict_path: str = ""):
        """[for better parsing, please download Please download mecab dic from https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md]
        
        Keyword Arguments:
            dict_path {str} -- [description] (default: {""})
        """
        self.dict_path = dict_path
        if dict_path=="":
            self.mecab = MeCab.Tagger()
        else:
            self.mecab = MeCab.Tagger(f'-d {dict_path}')

    def parse(self, sentence: str):
        """[summary]
        
        Arguments:
            sentence {str} -- [description]
        
        Returns:
            [type] -- [description]
        """
        def _to_result(mecab_result: str):
            _w1 = mecab_result.split("\t")
            _w2 = _w1[1].split(",")
            word = _w1[0]
            word_type = _w2[0]
            word_kana = _w2[-1]
            return MecabResult(word=word,
                               word_type=word_type,
                               word_kana=word_kana)

        return list(map(lambda r: _to_result(r), self.mecab.parse(sentence).splitlines()[:-1]))

    def async_par_parse(self, sentences: List[str]):
        """[TBD]
        
        Arguments:
            sentences {List[str]} -- [description]
        """
        pass
