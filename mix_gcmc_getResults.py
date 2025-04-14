# -*- coding: utf-8 -*
### 本脚本用于获取gRASPA单组份吸附模拟结果 ###
### Xie Qilin 2025.04.14 ###

## 获取双组分吸附等温线数据，目录结构：材料-分子1-分子2-温度-压力/output.txt
import os
import pandas as pd

work_dir = "/home/user/gRASPA/single_isotherm"  # 替换为你的主目录路径
output_csv_file = "/home/user/gRASPA/single_isotherm/results.csv"  # 输出的 CSV 文件名

def parse_output_file(file_path):
    """
    解析单个 output.txt 文件，提取甲烷的平均吸附热和吸附量。
    """
    with open(file_path, 'r') as file:
        content = file.readlines()

    # 提取材料名、分子名、温度和压力
    dir_path = os.path.dirname(file_path)
    parts = dir_path.split(os.sep)  # 按路径分隔符分割
    material_name = parts[-5]
    molecule1_name = parts[-4]
    molecule2_name = parts[-3]
    temperature_part = parts[-2]
    pressure_part = parts[-1]

    # 解析温度和压力
    temperature = float(temperature_part[1:-1])  # 去掉 T 和 K
    pressure = float(pressure_part[1:-3])  # 去掉 P 和 bar

    # 提取平均吸附热 (HEAT OF ADSORPTION)
    for i, line in enumerate(content):
        if "BLOCK AVERAGES (HEAT OF ADSORPTION: kJ/mol)" in line:
            avg_heat_of_adsorption1 = float(content[i+7].split(',')[0].split()[-1].strip())
            avg_heat_of_adsorption2 = float(content[i+15].split(',')[0].split()[-1].strip())
            break
        
    # 提取不同单位的平均吸附量
    loading_units = {
        "# MOLECULES 1": None,
        'Framework mass': None,
        "mg/g 1": None,
        "mol/kg 1": None,
        "g/L 1": None,
        '# MOLECULES 2': None,
        'mg/g 2': None,
        'mol/kg 2': None,
        'g/L 2': None
    }

    for i, line in enumerate(content):
        if 'BLOCK AVERAGES (LOADING: # MOLECULES)' in line:
            loading_units["# MOLECULES 1"] = float(content[i+16].split(',')[0].split()[-1].strip())
            loading_units["# MOLECULES 2"] = float(content[i+25].split(',')[0].split()[-1].strip())
        if 'BLOCK AVERAGES (LOADING: mg/g)' in line:

            loading_units['Framework mass'] = float(content[i+3].split(' ')[3].strip())

            loading_units["mg/g 1"] = float(content[i+19].split(',')[0].split()[-1].strip())
            loading_units["mg/g 2"] = float(content[i+29].split(',')[0].split()[-1].strip())
        if 'BLOCK AVERAGES (LOADING: mol/kg)' in line:
            loading_units["mol/kg"] = float(content[i+19].split(',')[0].split()[-1].strip())
            loading_units["mol/kg 2"] = float(content[i+29].split(',')[0].split()[-1].strip())
        if 'BLOCK AVERAGES (LOADING: g/L)' in line:
            loading_units["g/L 1"] = float(content[i+8].split(',')[0].split()[-1].strip())
            loading_units["g/L 2"] = float(content[i+17].split(',')[0].split()[-1].strip())


    return {
        "materials": material_name,
        "mol1": molecule1_name,
        "mol2": molecule2_name,
        "T/K": int(temperature),
        "P/bar": pressure,
        "adsorption_heat1": avg_heat_of_adsorption1,
        "adsorption_heat2": avg_heat_of_adsorption2,
        "loading_molecules1": loading_units["# MOLECULES 1"],
        "loading_molecules2": loading_units["# MOLECULES 2"],
        "loading_mg/g1": loading_units["mg/g 1"],
        "loading_mg/g2": loading_units["mg/g 2"],
        "loading_mol/kg1": loading_units["mol/kg"],
        "loading_mol/kg2": loading_units["mol/kg 2"],
        "loading_g/L1": loading_units["g/L 1"],
        "loading_g/L2": loading_units["g/L 2"],
        "loading_framework_mass": loading_units['Framework mass'],
    }

def process_directory(root_dir):
    """
    遍历根目录下的所有 output.txt 文件并解析，将结果存储为 DataFrame。
    """
    results = []

    # 遍历目录结构
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == "output.txt":
                file_path = os.path.join(root, file)
                result = parse_output_file(file_path)
                results.append(result)

    # 构建 DataFrame
    df = pd.DataFrame(results)

    return df

def save_to_csv(df, output_csv):
    """
    先将 DataFrame按照材料名、分子名、温度和压力排序，然后将 DataFrame 保存为 CSV 文件。
    """
    df = df.sort_values(by=["materials", "mol1", "mol2", "T/K", "P/bar"])
    df.to_csv(output_csv, index=False)


# 处理目录并保存结果
df = process_directory(work_dir)
save_to_csv(df, output_csv_file)