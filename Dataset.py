import time
import random
import numpy as np
from tqdm import tqdm
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

def data_load(dataset, has_v=True, has_a=True, has_t=True):
    # dir_str = './Data/' + dataset
    # train_edge = np.load(dir_str+'/train.npy', allow_pickle=True)
    # user_item_dict = np.load(dir_str+'/user_item_dict.npy', allow_pickle=True).item()

    dir_str = os.path.join(os.getcwd(), 'Data', dataset)
    train_edge = np.load(dir_str+'/train_sample.npy', allow_pickle=True)
    user_item_dict = np.load(os.path.join(dir_str, 'user_item_dict_sample.npy'), allow_pickle=True).item()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if dataset == 'movielens':
        num_user = 100
        # num_item = 1141
        # v_feat = np.load(dir_str+'/FeatureVideo_normal.npy', allow_pickle=True) if has_v else None
        # a_feat = np.load(dir_str+'/FeatureAudio_avg_normal.npy', allow_pickle=True) if has_a else None
        # t_feat = np.load(dir_str+'/FeatureText_stl_normal.npy', allow_pickle=True) if has_t else None
        v_feat = np.load(dir_str+'/v_feat_sample.npy', allow_pickle=True) if has_v else None
        a_feat = np.load(dir_str+'/a_feat_sample.npy', allow_pickle=True) if has_a else None
        t_feat = np.load(dir_str+'/t_feat_sample.npy', allow_pickle=True) if has_t else None
        v_feat = torch.tensor(v_feat, dtype=torch.float).to(device) if has_v else None
        a_feat = torch.tensor(a_feat, dtype=torch.float).to(device) if has_a else None
        t_feat = torch.tensor(t_feat, dtype=torch.float).to(device) if has_t else None

        num_item = v_feat.shape[0]
    # if dataset == 'tiktok':
    #     # tiktok_mmssl
    #     num_user = 9308
    #     # num_item = 1141
    #     # v_feat = np.load(dir_str+'/FeatureVideo_normal.npy', allow_pickle=True) if has_v else None
    #     # a_feat = np.load(dir_str+'/FeatureAudio_avg_normal.npy', allow_pickle=True) if has_a else None
    #     # t_feat = np.load(dir_str+'/FeatureText_stl_normal.npy', allow_pickle=True) if has_t else None
    #     v_feat = np.load(dir_str+'/image_feat.npy', allow_pickle=True) if has_v else None
    #     a_feat = np.load(dir_str+'/audio_feat.npy', allow_pickle=True) if has_a else None
    #     t_feat = np.load(dir_str+'/text_feat.npy', allow_pickle=True) if has_t else None
    #     v_feat = torch.tensor(v_feat, dtype=torch.float).to(device) if has_v else None
    #     a_feat = torch.tensor(a_feat, dtype=torch.float).to(device) if has_a else None
    #     t_feat = torch.tensor(t_feat, dtype=torch.float).to(device) if has_t else None

    #     num_item = v_feat.shape[0]

    elif dataset == 'tiktok':
        num_user = 36656
        
        if has_v:
            print(dir_str+'/image_feat.pt')
            v_feat = torch.load(dir_str+'/image_feat.pt')
            v_feat = torch.tensor(v_feat, dtype=torch.float).to(device)
        else:
            v_feat = None

        if has_a:
            a_feat = torch.load(dir_str+'/audio_feat.pt')
            a_feat = torch.tensor(a_feat, dtype=torch.float).to(device)
        else:
            a_feat = None
        
        t_feat = torch.load(dir_str+'/text_feat.pt') if has_t else None
        num_item = v_feat.shape[0]
    elif dataset == 'Kwai':
        num_user = 7010
        num_item = 86483
        v_feat = torch.load(dir_str+'/feat_v.npy')
        v_feat = torch.tensor(v_feat, dtype=torch.float).cuda()
        a_feat = t_feat = None
    elif dataset == 'sports':
        num_user = 35598
        # num_item = 1141
        # v_feat = np.load(dir_str+'/FeatureVideo_normal.npy', allow_pickle=True) if has_v else None
        # a_feat = np.load(dir_str+'/FeatureAudio_avg_normal.npy', allow_pickle=True) if has_a else None
        # t_feat = np.load(dir_str+'/FeatureText_stl_normal.npy', allow_pickle=True) if has_t else None
        v_feat = np.load(dir_str+'/image_feat.npy', allow_pickle=True) if has_v else None
        # a_feat = np.load(dir_str+'/a_feat_sample.npy', allow_pickle=True) if has_a else None
        t_feat = np.load(dir_str+'/text_feat.npy', allow_pickle=True) if has_t else None
        v_feat = torch.tensor(v_feat, dtype=torch.float).to(device) if has_v else None
        # a_feat = torch.tensor(a_feat, dtype=torch.float).to(device) if has_a else None
        t_feat = torch.tensor(t_feat, dtype=torch.float).to(device) if has_t else None

        num_item = v_feat.shape[0]

    return num_user, num_item, train_edge, user_item_dict, v_feat, a_feat, t_feat

class TrainingDataset(Dataset):
    def __init__(self, num_user, num_item, user_item_dict, edge_index):
        self.edge_index = edge_index
        self.num_user = num_user
        self.num_item = num_item
        self.user_item_dict = user_item_dict
        self.all_set = set(range(num_user, num_user+num_item))

    def __len__(self):
        # print("self.edge_index = ", self.edge_index)
        # print("type(self.edge_index) = ", type(self.edge_index))
        # print("len", len(self.edge_index))
        
        
        
        return len(self.edge_index)

    def __getitem__(self, index):
        user, pos_item = self.edge_index[index]
        while True:
            neg_item = random.sample(self.all_set, 1)[0]
            if neg_item not in self.user_item_dict[user]:
                break
        return torch.LongTensor([user,user]), torch.LongTensor([pos_item, neg_item])
