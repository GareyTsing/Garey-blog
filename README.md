# 机器学习与分子模拟学习笔记

## gRASPA学习笔记
### gRASPA介绍
1. 截至2025年4月，gRASPA暂无法适用于柔性分子；
2. 相比于RASPA，gRASPA的容错率更低，有许多需要特别注意的地方；
3. gRASPA的模拟，必须将所有力场文件、材料与分子定义文件、模拟输入文件放在一个目录中；
4. gRASPA的模拟目录中，必须包含force_field.def，即使不需要使用；
5. gRASPA的模拟目录中，pseudo_atoms.def和force_field_mixing_rules.def文件中的力场定义顺序和数量，必须完全一致；
6. gRASPA的simulaiton.input文件中，必须包含FugacityCoefficient参数；
7. gRASPA执行单组份模拟时，simulaiton.input文件中不得包含MolFraction参数；
8. gRASPA的分子定义文件mol.def中,Alkane-group必须是rigid，即刚性；
9. 同样的，刚性分子的Bond stretch为RIGID_BOND，通常不包含键角、二面角等信息；
10. gRASPA的执行命令是在模拟目录下，执行'xxx/src_clean/nvc_main.x'，xxx是gRASPA的目录。
### gRASPA脚本介绍
1. single_gcmc_generateFile.py 用于生成gRASPA单组份模拟的输入文件；生成模拟目录结构：材料名称-分子名称-T温度值K-P压力值bar；需要将所有力场文件、分子定义ff_files。
2. single_gcmc_getResults.py 用于批量获取gRASPA单组份模拟的计算结果，在workdir生成csv文件。
3. mix_gcmc_generateFile.py 用于生成gRASPA双组分组份模拟的输入文件；生成模拟目录结构：材料名称-分子1名称-分子2名称-T温度值K-P压力值bar；需要将所有力场文件、分子定义ff_files。
4. min_gcmc_getResults.py 用于批量获取gRASPA双组分组份模拟的计算结果，子啊workdir生成csv文件。
