import sys
from MelonDataset import SongTagDataset, SongTagGenreDataset
from arena_util import write_json, load_json
from get_autoencoder_scores import get_autoencoder_scores
from get_w2v_scores import get_w2v_scores
import argparse
from recommender import Recommender
import numpy as np

sim_measure = 'cos'
n_msp = 50
n_mtp = 90
freq_thr = 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-mode', type=int, help="local_val: 0, val: 1, test: 2", default=2)
    parser.add_argument('-retrain', type=int, help="remove tokenizer&w2v model and retrain 1: True, 0: False", default=0)
    args = parser.parse_args()
    _submit_type = args.mode
    _retrain = args.retrain

    if _submit_type == 0:  # split data에 대해서는 훈련 중간 중간 성능 확인을 위해서 question, answer 불러옴
        default_file_path = 'arena_data/'
        model_postfix = 'local_val'

        train_file_path = f'{default_file_path}/orig/train.json'
        question_file_path = f'{default_file_path}/questions/val.json'
        answer_file_path = f'{default_file_path}/answers/val.json'

        train_data = load_json(train_file_path)
        question_data = load_json(question_file_path)
        model_file_path = "model/autoencoder_450_256_0.0005_0.2_2_local_val.pkl"

    elif _submit_type == 1:
        default_file_path = 'res'
        model_postfix = 'val'

        train_file_path = f'{default_file_path}/train.json'
        val_file_path = f'{default_file_path}/val.json'
        train_data = load_json(train_file_path) + load_json(val_file_path)
        question_data = load_json(val_file_path)
        model_file_path = "model/autoencoder_450_256_0.0005_0.2_2_val.pkl"

    elif _submit_type == 2:
        default_file_path = 'res'
        model_postfix = 'test'

        train_file_path = f'{default_file_path}/train.json'
        val_file_path = f'{default_file_path}/val.json'
        test_file_path = f'{default_file_path}/test.json'
        train_data = load_json(train_file_path) + load_json(val_file_path) + load_json(val_file_path) + load_json(test_file_path)
        question_data = load_json(test_file_path)
        model_file_path = "model/autoencoder_450_256_0.0005_0.2_2_test.pkl"

    else:
        print('mode error! local_val: 0, val: 1, test: 2')
        sys.exit(1)

    # Autoencoder의 input: song, tag binary vector의 concatenate, tags는 str이므로 id로 변형할 필요 있음
    tag2id_file_path = f'{default_file_path}/tag2id_{model_postfix}.npy'
    id2tag_file_path = f'{default_file_path}/id2tag_{model_postfix}.npy'
    # Song이 너무 많기 때문에 frequency에 기반하여 freq_thr번 이상 등장한 곡들만 남김, 남은 곡들에게 새로운 id 부여
    prep_song2id_file_path = f'{default_file_path}/freq_song2id_thr{freq_thr}_{model_postfix}.npy'
    id2prep_song_file_path = f'{default_file_path}/id2freq_song_thr{freq_thr}_{model_postfix}.npy'

    get_autoencoder_scores(model_file_path, model_postfix)
    get_w2v_scores(model_postfix, _retrain)

    song_meta = load_json('res/song_meta.json')
    prep_song2id = dict(np.load(prep_song2id_file_path, allow_pickle=True).item())
    freq_song = set(prep_song2id.keys())

    rec_list = Recommender(train_data, question_data, n_msp, n_mtp, model_postfix, sim_measure, song_meta, freq_song, save=True)


