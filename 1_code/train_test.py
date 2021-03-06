from torch_geometric.data import Data, DataLoader
import torch
import torch.nn.functional as F
from torch.nn import Linear, MSELoss
from torch_geometric.nn import GCNConv, global_mean_pool, NNConv
import networkx as nx
import matplotlib.pyplot as plt
from torch_geometric.utils import to_networkx
from torch_geometric.datasets import TUDataset
from torch.utils.data.sampler import SubsetRandomSampler
from topo_data import Autopo, split_balance_data
import numpy as np
import math
import csv
from scipy import stats
from easydict import EasyDict
from model import CircuitGNN
from ml_utils import train, test, rse, initialize_model
import argparse


if __name__ == '__main__':

# ======================== Arguments ==========================#

    parser = argparse.ArgumentParser()

    parser.add_argument('-path', type=str, default="../0_rawdata", help='raw data path')
    parser.add_argument('-y_select', type=str, default='reg_eff',help='define target label')
    parser.add_argument('-batch_size', type=int, default=32, help='batch size')
    parser.add_argument('-n_epoch', type=int, default=10, help='number of training epoch')
    parser.add_argument('-gnn_nodes', type=int, default=100, help='number of nodes in hidden layer in GNN')
    parser.add_argument('-predictor_nodes', type=int, default=100, help='number of MLP predictor nodes at output of GNN') 
    parser.add_argument('-gnn_layers', type=int, default=3, help='number of layer')
    parser.add_argument('-model_index', type=int, default=0, help='model index')
    parser.add_argument('-threshold', type=float, default=0, help='classification threshold')
 
    args = parser.parse_args()

    path=args.path
    y_select=args.y_select
    data_folder='../2_dataset/'+y_select
    batch_size=args.batch_size
    n_epoch=args.n_epoch
    th=args.threshold
 
# ======================== Data & Model ==========================#

    dataset = Autopo(data_folder,path,y_select)

    train_loader, val_loader, test_loader = split_balance_data(dataset,y_select[:3]=='cls',batch_size)

    
    nf_size=4
    ef_size=3
    nnode=4
    if args.model_index==0:
        ef_size=6

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    data = dataset[0].to(device)
 
    model = initialize_model(args.model_index,args.gnn_nodes,args.predictor_nodes,args.gnn_layers,nf_size,ef_size,device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    criterion = MSELoss(reduction='mean').to(device)

# ========================= Train & Test ==========================#

    model = train(train_loader,val_loader, model, n_epoch, batch_size,nnode,device,args.model_index,optimizer)

    test(test_loader, model, n_epoch, batch_size, nnode, args.model_index, y_select[:3]=='cls',device,optimizer,th)



