import MeCab
from dataclasses import dataclass
from typing import Any, Iterable, List, Tuple, Callable
from asgiref.sync import sync_to_async
import asyncio

@dataclass(frozen=True)
class MecabResult:
    sencence: str
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

    def parse(self, sentence: str) -> MecabResult:
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
            return MecabResult(sencence=sentence,
                               word=word,
                               word_type=word_type,
                               word_kana=word_kana)

        return list(map(lambda r: _to_result(r), self.mecab.parse(sentence).splitlines()[:-1]))

    async def async_parse(self, sentences: List[str]) -> List[MecabResult]:
        """[TBD]
        
        Arguments:
            sentences {List[str]} -- [description]
        """
        async def _aync_parse(sentence: str):
            result = await sync_to_async(self.parse)(sentence)
            return result
        return await asyncio.gather(*[_aync_parse(sentence) for sentence in sentences])