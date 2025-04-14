# -*- coding: utf-8 -*
### 本脚本用于生成gRASPA单组份吸附模拟输入文件 ###
### Xie Qilin 2025.04.14 ###

##### 导入模块 ####
import os
import shutil
from itertools import product

#######################################################################################

##### 脚本说明 ####
"""
按照材料-分子-温度-压力的顺序统一生成RASPA输入和执行文件，以便于批量运行和读取；
workdir中会产生run.sh文件，使用 'bash run.sh' 命令可以运行所有的输入文件；
使用 'nohup bash run.sh > log.txt 2>&1 &' 命令可以在后台运行，log.txt中会记录日志信息；
"""

#### 当仅计算某个材料吸附等温线时，直接设置条件 ####
workdir = r'/home/user/gRASPA/project/'
ff_files = r'/home/user/gRASPA/ff_files'            # 力场文件路径；
materials=['IRMOF-1']                               # 材料名称必须与CIF文件名一致；若mat_dir存在，则无效；
temperatures=[298]                                  # 单位：K
pressures=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]   # 单位：bar
mol1s=['methane']               # 组分1名称
mol2s=['CO2']                   # 组分2名称

#### 定义分子 ####
'''批量计算不同分子组分，则设置more_mols为True,并设置分子的相关参数；
   否则设置more_mols为False,并在template中设置分子参数。'''

more_mols = False

IdealGasRosenbluthWeight1 = [1.0]
FugacityCoefficient1 = [1.0]
MolFraction1 = [0.95]

IdealGasRosenbluthWeight2 = [1.0]
FugacityCoefficient2 = [1.0]
MolFraction2 = [0.05]

#######################################################################################

#### 当计算许多材料吸附量时，需要指定保存cif文件的目录mat_dir ####
mat_dir = None                  # 材料CIF文件路径；若存在，则materials无效；

#### 获取材料名称 ####
def get_material_name(mat_dir):
    """ 获取目录中所有cif文件的文件名并保存为列表 """
    cif_files = [f for f in os.listdir(mat_dir) if f.endswith('.cif')]
    materials = []
    for cif_file in cif_files:
        # 去掉文件名中的.cif后缀
        material = cif_file[:-4]
        materials.append(material)
    return materials

if mat_dir:
    # 获取材料名称
    materials = get_material_name(mat_dir)

#######################################################################################

#### 力场文件等 ####

fixed_files = [
    'force_field.def',
    'force_field_mixing_rules.def',
    'pseudo_atoms.def'
]

#######################################################################################

#### 单组份吸附模拟输入文件模板 ####
""" Note：GCMC批量计算中，常见更改参数是温度和压力，其他参数一般不变； """

template = '''
NumberOfInitializationCycles 200000
NumberOfEquilibrationCycles  0
NumberOfProductionCycles     200000

UseMaxStep  yes
MaxStepPerCycle 1

UseChargesFromCIFFile yes

RestartFile no
RandomSeed  0

NumberOfTrialPositions 10
NumberOfTrialOrientations 10

NumberOfBlocks 1
AdsorbateAllocateSpace 10240
NumberOfSimulations 1
SingleSimulation yes

InputFileType cif
FrameworkName UIO_66_cc
UnitCells 0 1 1 1

ChargeMethod Ewald
Temperature  298
Pressure     100000

OverlapCriteria 1e5
CutOffVDW 18.0
CutOffCoulomb 18.0
EwaldPrecision 1e-6

Component 0 MoleculeName              methane
            IdealGasRosenbluthWeight  1.0
            FugacityCoefficient       1.0
            MolFraction               0.95
            TranslationProbability    1.0
            ReinsertionProbability    1.0
            IdentityChangeProbability 1.0
            SwapProbability           1.0
            CreateNumberOfMolecules   0

Component 1 MoleculeName              CO2
            IdealGasRosenbluthWeight  1.0
            FugacityCoefficient       1.0
            MolFraction               0.05
            RotationProbability       1.0
            TranslationProbability    1.0
            ReinsertionProbability    1.0
            IdentityChangeProbability 1.0
            SwapProbability           1.0
            CreateNumberOfMolecules   0
'''
template_line = template.split('\n')[1:]    # 去掉第一行空行

#### 生成输入文件 ####
for mat, mol1, mol2, t, p in product(materials, mol1s, mol2s, temperatures, pressures):
    dir = os.path.join(workdir,mat,mol1,mol2,f"T{t}K",f"P{p}bar")
    os.makedirs(dir, exist_ok=True)

    # 复制material.cif和mol.def
    # （假设文件名与材料名一致）
    cif_src = os.path.join(ff_files, f"{mat}.cif")
    cif_dst = os.path.join(dir, f"{mat}.cif")
    if os.path.exists(cif_src):
        shutil.copy(cif_src, cif_dst)
    else:
        print(f"Warning: CIF file not found for {mat}")

    mol_src = os.path.join(ff_files, f"{mol1}.def")
    mol_dst = os.path.join(dir, f"{mol1}.def")
    if os.path.exists(mol_src):
        shutil.copy(mol_src,mol_dst)
    else:
        print(f"Warning: MOL file not found for {mol1}")

    mol_src = os.path.join(ff_files, f"{mol2}.def")
    mol_dst = os.path.join(dir, f"{mol2}.def")
    if os.path.exists(mol_src):
        shutil.copy(mol_src,mol_dst)
    else:
        print(f"Warning: MOL file not found for {mol2}")
    
    # 复制其他固定文件
    for filename in fixed_files:
        src = os.path.join(ff_files, filename)
        dst = os.path.join(dir, filename)
        if os.path.exists(src):
            shutil.copy(src, dst)
        else:
            print(f"Warning: File not found {filename}")

    # 写入input文件
    file = os.path.join(dir, 'simulation.input')
    with open(file, 'w') as f:
        lines = template_line.copy()                # 复制模板行
        lines[21] = 'FrameworkName {}'.format(mat)  # 更新材料名称
        lines[25] = 'Temperature {}'.format(t)      # 更新温度
        lines[26] = 'Pressure {}e5'.format(p)       # 更新压力
        lines[33] = 'Component 0 MoleculeName              {}'.format(mol1)  # 更新分子1名称
        lines[43] = 'Component 1 MoleculeName              {}'.format(mol2)  # 更新分子2名称
        if more_mols:
            lines[34] = 'IdealGasRosenbluthWeight  {}'.format(IdealGasRosenbluthWeight1[mol1s.index(mol1)])
            lines[35] = 'FugacityCoefficient       {}'.format(FugacityCoefficient1[mol1s.index(mol1)])
            lines[36] = 'MolFraction               {}'.format(MolFraction1[mol1s.index(mol1)])
            lines[44] = 'IdealGasRosenbluthWeight  {}'.format(IdealGasRosenbluthWeight2[mol2s.index(mol2)])
            lines[45] = 'FugacityCoefficient       {}'.format(FugacityCoefficient2[mol2s.index(mol2)])
            lines[46] = 'MolFraction               {}'.format(MolFraction2[mol2s.index(mol2)])
        for line in lines:
            f.write(line)
            f.write('\n')
        f.close()

########################################################################################

#### run.py脚本 ####
script_content = f"""import os
import sys
from multiprocessing import Pool

execdir = r'/home/Xieql/packages/gRASPA-main/src_clean'
maindir = r'{workdir}'

materials = {materials}
mol1s = {mol1s}
mol2s = {mol2s}
temps = {temperatures}
pressures = {pressures}


def run_simulation(params):
    mat, mol1, mol2, t, p = params
    sim_dir = os.path.join(
        maindir,
        mat,
        mol1,
        mol2,
        f"T{{t}}K",
        f"P{{p}}bar"
    )
    
    if not os.path.exists(sim_dir):
        print(f"Directory not found: {{sim_dir}}")
        return

    try:
        # 切换到工作目录
        os.chdir(sim_dir)
        
        # 清理旧数据
        os.system("rm -rf AllData FirstBead Lambda Movies Restart TMMC")
        
        # 执行模拟并重定向输出
        cmd = f"{{execdir}}/nvc_main.x > output.txt 2>&1"
        exit_code = os.system(cmd)
        
        # 再次清理
        os.system("rm -rf AllData FirstBead Lambda Movies Restart TMMC")
        
        if exit_code != 0:
            print(f"Error in {{sim_dir}} (exit code: {{exit_code}})")
            return False
        return True
    except Exception as e:
        print(f"Exception in {{sim_dir}}: {{str(e)}}")
        return False

if __name__ == '__main__':
    # 生成所有参数组合
    param_combinations = []
    for mat in materials:
        for m1 in mol1s:
            for m2 in mol2s:
                for t in temps:
                    for p in pressures:
                        param_combinations.append((mat, m1, m2, t, p))

    # 创建进程池
    with Pool(processes=20) as pool:
        results = pool.imap_unordered(run_simulation, param_combinations)
        
        # 进度跟踪
        total = len(param_combinations)
        success = 0
        for i, result in enumerate(results, 1):
            if result:
                success += 1
            sys.stdout.write(f"\\rProgress: {{i}}/{{total}} | Success: {{success}} | Failed: {{i-success}}")
            sys.stdout.flush()

    print("\\n\\nAll tasks completed!")
    print(f"Success rate: {{success/total:.1%}}")
"""

with open(os.path.join(workdir, "run_all_simulations.py"), 'w') as f:
        f.write(script_content)
        f.close()

########################################################################################

""" run_path = os.path.join(workdir, "run_all_simulations.py")
os.system("nohup python {} > log.txt 2>&1 &".format(run_path)) """