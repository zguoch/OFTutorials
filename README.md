 

所有的写作都保存为.rst文件，在sphinx/source文件夹里面。
文件按照OF算例分级的逻辑进行分级，除了具体case文件夹，每个文件夹里面都应该有一个index.rst和map.dot文件作为引导。

**作者贡献，只需要在相应的目录下（完善中...）编写以与算例文件夹同名的rst文件，比如cavity.rst，其他的均不需要管，算例的结果（图片，动画等）全部保存在算例文件夹下面的results子文件夹里面，以便在rst文件中调用。**

**每个求解器的目录下应该有一个以求解器名称命名的rst文件，用作介绍此求解器的物理、数学、编程方面的细节**。

关于rst写作方面的注意事项及如何进行协作的技术细节正在整理中....

```bash
.
├── changelog.rst
├── include.rst_
├── incompressible
│   ├── icoFoam
│   │   ├── cavity
│   │   ├── cavity.rst
│   │   ├── icoFoam.rst
│   │   ├── index.rst
│   │   └── map.dot
│   ├── index.rst
│   └── map.dot
├── index.rst
├── manual.bib
├── map.dot
└── refs.rst
```
