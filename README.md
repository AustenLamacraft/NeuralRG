

# Real NVP 

## How to Run 

```python
#ring2D
python learn_realnvp.py -Batch 64 -Ntherm 10 -Nsteps 10 -Nskip 10 -Nlayers 4 -Hs 10 -Ht 10 -target ring2d -epsilon 1.0 -alpha 0.0 -beta 1.0 -delta 1.0 -omega 1.0 -Nepoch 5000 

#Ising
python learn_realnvp.py -Batch 64 -Ntherm 5 -Nsteps 1 -Nskip 0 -Nlayers 10 -Hs 4 -Ht 4 -target ising -T 2.5 -L 8 -d 2 -epsilon 1.0 -beta 1.0  -delta 1.0 -omega 0.0  -Nepoch 5000 -lr 0.001 -exact 0.177921 -train_model 

#TEBD
python learn_tebd.py -Batch 256 -Ntherm 0 -Nsteps 5 -Nskip 0 -Nlayers 8 -Hs 64 -Ht 64 -target ising -T 2.269 -L 4 -d 2 -epsilon 0.0 -beta 1.0  -delta 1.0 -omega 0.5  -Nepoch 500 -lr 0.001 -exact 0.761761 -train_model 

#MERA (To produce results in the paper)
#L=8 
python learn_mera.py -Batch 256 -Ntherm 0 -Nsteps 5 -Nskip 0 -Ndis 1 -Nlayers 8 -Hs 64 -Ht 64 -target ising -T 2.269185314213022 -L 8 -d 2 -epsilon 0.0 -beta 1.0  -delta 1.0 -omega 0.5  -Nepoch 5000 -lr 0.001 -exact 0.646769 -train_model 
#L=16
python learn_mera.py -Batch 256 -Ntherm 0 -Nsteps 5 -Nskip 0 -Ndis 1 -Nlayers 8 -Hs 64 -Ht 64 -target ising -T 2.269185314213022 -L 16 -d 2 -epsilon 0.0 -beta 1.0  -delta 1.0 -omega 0.5  -Nepoch 5000 -lr 0.001 -exact 0.544445 -train_model 
```

To check the results 

```python
#sample using the model
python learn_accratio.py -Batch 64 -Ntherm 5 -Nsteps 1 -Nskip 0 -Nlayers 10 -Hs 4 -Ht 4 -target ising -K 0.44068679350977147 -L 4 -d 2 -epsilon 1.0 -beta 1.0  -delta 1.0 -omega 0.0  -Nepoch 5000 -lr 0.01 -exact 0.371232 -modelname data/learn_acc/ising_L4_d2_K0.44068679350977147_Nl10_Hs4_Ht4_epsilon1.0_beta1.0_delta1.0_omega0.0_Batchsize64_Ntherm5_Nsteps1_Nskips0_lr0.01/epoch230

# plot proposed and accepted configurations
python plot_configs.py -f data/learn_acc/ising_L4_d2_K0.44068679350977147_Nl10_Hs4_Ht4_epsilon1.0_beta1.0_delta1.0_omega0.0_Batchsize64_Ntherm5_Nsteps1_Nskips0_lr0.01_mc.h5 

```

### Exact Ising results 



| $d=1,T=4.0$ |         PBC         | OBC  |
| :---------: | :-----------------: | :--: |
|    $L=8$    | 0.206153+/-0.000317 |      |
|             |                     |      |
|             |                     |      |



| $d=1,T=2.0$ |         PBC         | OBC  |
| :---------: | :-----------------: | :--: |
|    $L=8$    | 0.338189+/-0.000352 |      |
|             |                     |      |
|             |                     |      |



| $d=1,T=2.5$ |          PBC          |         OBC          |
| :---------: | :-------------------: | :------------------: |
|    $L=8$    |  0.277838+/-0.000294  |                      |
|   $L=16$    |  0.138871+/-0.000273  | 0.130933+/-0.000262  |
|   $L=64$    | 0.0344761+/-0.0001465 | 0.0341328+/-0.000158 |



| $d=2,T= T_c(2.269185314213022)$ |          PBC          |          OBC          |
| :-----------------------------: | :-------------------: | :-------------------: |
|              $L=2$              |                       | 0.56882 +/- 0.000409  |
|              $L=4$              | 0.761761 +/- 0.000421 | 0.371232 +/- 0.000429 |
|              $L=6$              | 0.693504 +/- 0.000436 | 0.30321 +/- 0.000397  |
|              $L=8$              | 0.646769 +/- 0.000445 | 0.266751 +/- 0.00038  |
|             $L=16$              |  0.544445+/-0.000487  |                       |
|             $L=32$              |  0.458427+/-0.000474  |                       |
|             $L=64$              |                       |                       |

| $d=2,T=2.5$ |          PBC          |          OBC           |
| :---------: | :-------------------: | :--------------------: |
|    $L=4$    | 0.654539 +/- 0.000478 |   0.309222+/-0.0004    |
|    $L=8$    |  0.431992+/-0.000521  | 0.177921 +/- 0.000304  |
|   $L=16$    |  0.202231+/-0.000392  | 0.0905703 +/- 0.000219 |






