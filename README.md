

所有的写作都保存为.rst文件，在sphinx/source文件夹里面。
文件按照OF算例分级的逻辑进行分级，除了具体case文件夹，每个文件夹里面都应该有一个index.rst和map.dot文件作为引导。


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