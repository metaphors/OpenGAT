from datasets import GeneratorBasedBuilder
from datasets import DatasetInfo, Features, Value, ClassLabel
from datasets import DownloadManager, SplitGenerator, Split


class AdvTNCCTitle(GeneratorBasedBuilder):
    def _info(self):
        return DatasetInfo(
            features=Features({
                "text": Value("string"),
                "label": ClassLabel(
                    names=[
                        "Politics",
                        "Economics",
                        "Education",
                        "Tourism",
                        "Environment",
                        "Language",
                        "Literature",
                        "Religion",
                        "Arts",
                        "Medicine",
                        "Customs",
                        "Instruments"
                    ]
                )
            })
        )

    def _split_generators(self, dl_manager: DownloadManager):
        return [
            SplitGenerator(
                name=Split.TEST,
                gen_kwargs={
                    "filepath": "data/Dataset.AdvTS/Adv.TNCC-title.txt"
                }
            )
        ]

    def _generate_examples(self, filepath):
        with open(filepath, encoding="utf-8") as file:
            for index, line in enumerate(file):
                yield index, {
                    "text": line.strip().split('\t')[2],
                    "label": line.strip().split('\t')[0]
                }
