# -*- coding: utf-8 -*-
"""
    pygments.lexers.foam
    ~~~~~~~~~~~~~~~~~~~~~

    Lexers for Gmsh languages based on Cpp lexer of pygments.

    :copyright: Copyright 2020-2020 by the Zhikui Guo.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, include, bygroups, using, \
    this, inherit, default, words
from pygments.util import get_bool_opt
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Error

__all__ = ['GmshLexer']


class CFamilyLexer(RegexLexer):
    """
    For C family source code.  This is used as a base class to avoid repetitious
    definitions.
    """

    #: optional Comment or Whitespace
    _ws = r'(?:\s|//.*?\n|/[*].*?[*]/)+'

    # The trailing ?, rather than *, avoids a geometric performance drop here.
    #: only one /* */ style comment
    _ws1 = r'\s*(?:/[*].*?[*]/\s*)?'

    tokens = {
        'whitespace': [
            # preprocessor directives: without whitespace
            (r'^#if\s+0', Comment.Preproc, 'if0'),
            ('^#', Comment.Preproc, 'macro'),
            # or with whitespace
            ('^(' + _ws1 + r')(#if\s+0)',
             bygroups(using(this), Comment.Preproc), 'if0'),
            ('^(' + _ws1 + ')(#)',
             bygroups(using(this), Comment.Preproc), 'macro'),
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text),  # line continuation
            (r'//(\n|[\w\W]*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*][\w\W]*?[*](\\\n)?/', Comment.Multiline),
            # Open until EOF, so no ending delimeter
            (r'/(\\\n)?[*][\w\W]*', Comment.Multiline),
        ],
        'statements': [
            (r'(L?)(")', bygroups(String.Affix, String), 'string'),
            (r"(L?)(')(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])(')",
             bygroups(String.Affix, String.Char, String.Char, String.Char)),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[LlUu]*', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[LlUu]*', Number.Hex),
            (r'0[0-7]+[LlUu]*', Number.Oct),
            (r'\d+[LlUu]*', Number.Integer),
            (r'\*/', Error),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'[()\[\],.]', Punctuation),
            (words(('asm', 'auto', 'break', 'case', 'const', 'continue',
                    'default', 'do', 'else', 'enum', 'extern', 'for', 'goto',
                    'if', 'register', 'restricted', 'return', 'sizeof',
                    'static', 'struct', 'switch', 'typedef', 'union',
                    'volatile', 'while'),
                   suffix=r'\b'), Keyword),
            (r'(bool|int|long|float|short|double|char|unsigned|signed|void)\b',
             Keyword.Type),
            (words(('inline', '_inline', '__inline', 'naked', 'restrict',
                    'thread', 'typename'), suffix=r'\b'), Keyword.Reserved),
            # Vector intrinsics
            (r'(__m(128i|128d|128|64))\b', Keyword.Reserved),
            # Microsoft-isms
            (words((
                'asm', 'int8', 'based', 'except', 'int16', 'stdcall', 'cdecl',
                'fastcall', 'int32', 'declspec', 'finally', 'int64', 'try',
                'leave', 'wchar_t', 'w64', 'unaligned', 'raise', 'noop',
                'identifier', 'forceinline', 'assume'),
                prefix=r'__', suffix=r'\b'), Keyword.Reserved),
            (r'(true|false|NULL)\b', Name.Builtin),
            (r'([a-zA-Z_]\w*)(\s*)(:)(?!:)', bygroups(Name.Label, Text, Punctuation)),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'root': [
            include('whitespace'),
            # functions
            (r'((?:[\w*\s])+?(?:\s|[*]))'  # return arguments
             r'([a-zA-Z_]\w*)'             # method name
             r'(\s*\([^;]*?\))'            # signature
             r'([^;{]*)(\{)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation),
             'function'),
            # function declarations
            (r'((?:[\w*\s])+?(?:\s|[*]))'  # return arguments
             r'([a-zA-Z_]\w*)'             # method name
             r'(\s*\([^;]*?\))'            # signature
             r'([^;]*)(;)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation)),
            default('statement'),
        ],
        'statement': [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'function': [
            include('whitespace'),
            include('statements'),
            (';', Punctuation),
            (r'\{', Punctuation, '#push'),
            (r'\}', Punctuation, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|'
             r'u[a-fA-F0-9]{4}|U[a-fA-F0-9]{8}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
            (r'\\\n', String),  # line continuation
            (r'\\', String),  # stray backslash
        ],
        'macro': [
            (r'(include)(' + _ws1 + r')([^\n]+)',
             bygroups(Comment.Preproc, Text, Comment.PreprocFile)),
            (r'[^/\n]+', Comment.Preproc),
            (r'/[*](.|\n)*?[*]/', Comment.Multiline),
            (r'//.*?\n', Comment.Single, '#pop'),
            (r'/', Comment.Preproc),
            (r'(?<=\\)\n', Comment.Preproc),
            (r'\n', Comment.Preproc, '#pop'),
        ],
        'if0': [
            (r'^\s*#if.*?(?<!\\)\n', Comment.Preproc, '#push'),
            (r'^\s*#el(?:se|if).*\n', Comment.Preproc, '#pop'),
            (r'^\s*#endif.*?(?<!\\)\n', Comment.Preproc, '#pop'),
            (r'.*?\n', Comment),
        ]
    }

    stdlib_types = {
        'size_t', 'ssize_t', 'off_t', 'wchar_t', 'ptrdiff_t', 'sig_atomic_t', 'fpos_t',
        'clock_t', 'time_t', 'va_list', 'jmp_buf', 'FILE', 'DIR', 'div_t', 'ldiv_t',
        'mbstate_t', 'wctrans_t', 'wint_t', 'wctype_t'}
    c99_types = {
        '_Bool', '_Complex', 'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint8_t',
        'uint16_t', 'uint32_t', 'uint64_t', 'int_least8_t', 'int_least16_t',
        'int_least32_t', 'int_least64_t', 'uint_least8_t', 'uint_least16_t',
        'uint_least32_t', 'uint_least64_t', 'int_fast8_t', 'int_fast16_t', 'int_fast32_t',
        'int_fast64_t', 'uint_fast8_t', 'uint_fast16_t', 'uint_fast32_t', 'uint_fast64_t',
        'intptr_t', 'uintptr_t', 'intmax_t', 'uintmax_t'}
    linux_types = {
        'clockid_t', 'cpu_set_t', 'cpumask_t', 'dev_t', 'gid_t', 'id_t', 'ino_t', 'key_t',
        'mode_t', 'nfds_t', 'pid_t', 'rlim_t', 'sig_t', 'sighandler_t', 'siginfo_t',
        'sigset_t', 'sigval_t', 'socklen_t', 'timer_t', 'uid_t'}

    def __init__(self, **options):
        self.stdlibhighlighting = get_bool_opt(options, 'stdlibhighlighting', True)
        self.c99highlighting = get_bool_opt(options, 'c99highlighting', True)
        self.platformhighlighting = get_bool_opt(options, 'platformhighlighting', True)
        RegexLexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
                RegexLexer.get_tokens_unprocessed(self, text):
            if token is Name:
                if self.stdlibhighlighting and value in self.stdlib_types:
                    token = Keyword.Type
                elif self.c99highlighting and value in self.c99_types:
                    token = Keyword.Type
                elif self.platformhighlighting and value in self.linux_types:
                    token = Keyword.Type
            yield index, token, value

class GmshLexer(CFamilyLexer):
    """
    For Gmsh script code with preprocessor directives.
    """
    name = 'Gmsh'
    aliases = ['Gmsh', 'gmsh']
    filenames = ['*.geo']
    mimetypes = ['text/x-c++hdr', 'text/x-c++src']
    priority = 0.1

    tokens = {
        'statements': [
            (words((
                'Include','For','If','Else','While','In','EndFor','EndWhile','EndIf','Else','ElseIf',
                'Pi','GMSH_MAJOR_VERSION','GMSH_MINOR_VERSION','GMSH_PATCH_VERSION','MPI_Size','MPI_Rank','Cpu','Memory','TotalMemory','newp','newl','news','newv','newll','newsl','newreg','Exit','DefineConstant','DefineNumber','DefineString','SetString','Abort','CreateDir','Printf','Warning','ShapeFromFile','Draw','SetChanged','BoundingBox','Model','Physicals','Variables','Options','Print','Sleep','SystemCall','NonBlockingSystemCall','OnelabRun','SetName',
                'SetFactory','BooleanIntersection','BooleanUnion','BooleanDifference','BooleanFragments','Delete','SyncModel','NewModel'
                ), suffix=r'\b'), Keyword),
            (r'(Geometry\\.TransformYX|Sphere|Mesh\\.ToleranceEdgeLength|computeCohomology|intersect|View\\.Stipple9|General\\.AxesLabelY|General\\.RecentFile9|Cone|ENABLE_PETSC|Mesh\\.Color\\.Triangles|General\\.Clip3B|Mesh\\.PartitionTopologyFile|getColor|Print\\.GifSort|ENABLE_MPI|Geometry\\.ExtrudeReturnLateralEntities|ENABLE_PLUGINS|Mesh\\.Recombine3DLevel|ENABLE_HXT|Mesh\\.NbPrisms|Solver\\.Name5|View\\.FileName|General\\.OptionsPositionX|View\\.AxesFormatZ|getPeriodicNodes|General\\.VectorType|Solver\\.Name7|View\\.GeneralizedRaiseFactor|Geometry\\.SnapX|View\\.Color\\.Lines|General\\.Version|Geometry\\.Transform|setPeriodic|View\\.SaturateValues|Ellipse|PostProcessing\\.HorizontalScales|Chamfer|View\\.TensorType|probe|Mesh\\.PointNumbers|General\\.WatchFilePattern|Print\\.ParameterCommand|addEllipseArc|General\\.MenuWidth|General\\.Stereo|Threshold|Geometry\\.DoubleClickedVolumeCommand|Geometry\\.PointSize|PartitionMesh|addTorus|General\\.TrackballQuaternion2|run|View\\.IntervalsType|Geometry\\.LabelType|General\\.AxesMikado|Physical Surface|Mesh\\.CharacteristicLengthFromPoints|Solver\\.Name2|Solver\\.ShowInvisibleParameters|View\\.MaxRecursionLevel|General\\.Light2Y|merge|ReverseMesh Curve | Surface|Combine TimeStepsFromAllViews|Mesh\\.StlOneSolidPerSurface|Periodic Curve|Mesh\\.PartitionLineWeight|View\\.TransformXX|getEntitiesInBoundingBox|AdaptMesh|Cylinder|General\\.Light2X|importShapes|Acos|addCircle|Geometry\\.OffsetY|General\\.Clip1C|Log|Mesh\\.NbTriangles|getModelData|Mesh\\.PointSize|Tan|getCenterOfMass|General\\.MenuHeight|Solver\\.Executable4|General\\.ScaleY|setCoordinates|General\\.ExtraHeight|General\\.Antialiasing|Call|Mesh\\.MetisRefinementAlgorithm|Symmetry|General\\.Color\\.Foreground|View\\.DrawTriangles|General\\.RecentFile0|General\\.Light1|View\\.ColormapCurvature|Geometry\\.LineType|Print\\.PostElementary|setNumber|Solver\\.Extension1|partition|wait|General\\.QuadricSubdivisions|Geometry\\.Color\\.Points|SendToServer View|View\\.Visible|Geometry\\.PointType|ENABLE_OPENMP|Geometry\\.ToleranceBoolean|View\\.TimeStep|ENABLE_BUILD_DYNAMIC|Geometry\\.TransformZX|General\\.BackgroundImageFileName|View\\.Stipple8|getJacobians|Mesh\\.LightTwoSide|General\\.ExtraPositionY|BoundaryLayer|Geometry\\.Color\\.Projection|Affine|Smoother Surface|ENABLE_CGNS|General\\.CameraFocalLengthRatio|Mesh\\.CrossFieldClosestPoint|General\\.Clip2B|General\\.AxesFormatX|Mesh\\.PartitionCreateGhostCells|Geometry\\.Color\\.Surfaces|ENABLE_PRIVATE_API|Show|Mesh\\.Color\\.Prisms|Print\\.PostSICN|draw|ENABLE_NUMPY|General\\.Trackball|Mesh\\.CharacteristicLengthMax|General\\.Light5|Mesh\\.Renumber|General\\.Clip4A|Mesh\\.SecondOrderIncomplete|Mesh\\.Triangles|Volume|View\\.ColormapAlphaPower|Print\\.GeoOnlyPhysicals|setMeshSize|unpartition|General\\.Light5Z|Combine ElementsByViewName|Print\\.TexAsEquation|View\\.ArrowSizeMin|View\\.AxesLabelY|View\\.DrawTensors|View\\.Light|cut|Dilate|General\\.ProgressMeterStep|Structured|PostProcessing\\.ForceElementData|View\\.AxesMinZ|preallocateJacobians|View\\.DisplacementFactor|ENABLE_BLAS_LAPACK|addDiscreteEntity|Extrude|ENABLE_METIS|Geometry\\.OCCSewFaces|addBezier|Mesh\\.NbPyramids|General\\.AxesValueMaxZ|General\\.PluginHeight|View\\.ColormapInvert|General\\.Light1W|General\\.SaveSession|Mesh\\.Color\\.Tetrahedra|Mesh\\.HighOrderDistCAD|Rotate|addLine|General\\.RecentFile6|Mesh\\.Smoothing|Mesh\\.HighOrderPoissonRatio|Mesh\\.MetisAlgorithm|Mesh\\.ElementOrder|General\\.Light5Y|Mesh\\.FlexibleTransfinite|AliasWithOptions View|Geometry\\.Light|Homology|View\\.GeneralizedRaiseView|General\\.AxesValueMinY|General\\.FileName|getPhysicalGroups|View\\.DrawPoints|Asin|CreateTopology|Mesh\\.QualityInf|Point|General\\.AxesLabelX|Geometry\\.Color\\.Lines|Geometry\\.Normals|General\\.MessageHeight|Combine TimeStepsByViewName | Combine TimeSteps|General\\.RecentFile2|Geometry\\.OCCFixDegenerated|getVisibility|Solver\\.RemoteLogin4|View\\.TransformYY|clear|Mesh\\.Recombine3DAll|Print\\.PgfExportAxis|Mesh\\.VolumeEdges|General\\.CameraAperture|Geometry\\.OldCircle|Solver\\.AutoMergeFile|Mesh\\.RadiusInf|View\\.RangeType|Mesh\\.PartitionCreatePhysicals|View\\.ColormapNumber|setOrder|View\\.TransformZX|General\\.Clip0D|Geometry\\.TransformZY|Delete Empty Views|General\\.ErrorFileName|Solver\\.AutoShowViews|General\\.ExpertMode|getMass|General\\.Clip4D|Print\\.Parameter|View\\.Type|PostProcessing\\.CombineRemoveOriginal|View\\.Stipple4|General\\.AxesForceValue|Print\\.ParameterFirst|Return|General\\.ClipOnlyVolume|Save|ENABLE_MED|General\\.TranslationY|General\\.MaxZ|General\\.ArrowStemRadius|setTransfiniteSurface|View\\.ComponentMap3|Mesh\\.HighOrderIterMax|View\\.Color\\.Quadrangles|View\\.NbIso|General\\.Clip1B|Solver\\.RemoteLogin0|getBoundary|General\\.FastRedraw|selectEntities|View\\.ComponentMap5|Solver\\.Executable0|Print\\.EpsPS3Shading|BooleanDifference|Print\\.JpegSmoothing|General\\.FieldPositionX|lock|Save View|Solver\\.Executable2|Physical Curve|Geometry\\.PointNumbers|Geometry\\.SurfaceNumbers|fillet|addPoint|General\\.Clip5B|General\\.Light0Z|addCone|setReverse|addPipe|Mesh\\.CgnsConstructTopology|Geometry\\.Color\\.Normals|Print\\.Height|Mesh\\.CharacteristicLengthMin|View\\.Boundary|ENABLE_GMM|Geometry\\.LightTwoSide|Geometry\\.ExtrudeSplinePoints|General\\.HighOrderToolsPositionX|Mesh\\.MaxNumThreads1D|View\\.SmoothNormals|General\\.AxesFormatZ|General\\.Color\\.AmbientLight|View\\.Color\\.Text2D|Print\\.PostDisto|View\\.MinVisible|Mesh\\.Dual|General\\.Color\\.BackgroundGradient|getType|Geometry\\.ExactExtrusion|View\\.LineType|Mesh\\.SurfaceNumbers|RefineMesh|unlock|Solver\\.RemoteLogin2|Solver\\.Name1|General\\.TrackballQuaternion0|SetOrder|View\\.Tangents|addNodes|General\\.StatisticsPositionX|Mesh\\.LineNumbers|Geometry\\.SnapZ|Background Field =|Geometry\\.PointSelectSize|Mesh\\.NbHexahedra|View\\.Color\\.Pyramids|View\\.Color\\.Triangles|General\\.AxesTicsX|copy|General\\.ManipulatorPositionY|General\\.StatisticsPositionY|Mesh\\.LabelSampling|Mesh\\.MaxNumThreads3D|Geometry\\.TransformYY|Mesh\\.PartitionQuadWeight|Octree|General\\.PointSize|Param|PointsOf|PostProcessing\\.AnimationDelay|getMatrixOfInertia|Solver\\.Executable3|General\\.BackgroundImage3D|View\\.DrawTrihedra|General\\.ContextPositionX|addSphere|General\\.GraphicsPositionX|getTags|ENABLE_ALGLIB|ENABLE_PROFILE|View\\.OffsetY|Alias View|View\\.Sampling|View\\.TransformYX|Mesh\\.Light|getDerivative|set|View\\.Color\\.Hexahedra|Mesh\\.AngleToleranceFacetOverlap|View\\.Color\\.Tangents|View\\.MaxVisible|Combine ElementsFromVisibleViews|Mesh\\.SmoothRatio|General\\.PolygonOffsetFactor|Solver\\.Name8|PostProcessing\\.Plugins|getBarycenters|View\\.ShowScale|View\\.DrawQuadrangles|Mesh\\.MetisObjective|General\\.FltkTheme|getElement|Mesh\\.MinimumCirclePoints|ENABLE_KBIPACK|ENABLE_MPEG_ENCODE|General\\.Shininess|View\\.AxesMinX|General\\.Camera|Geometry\\.Color\\.Tangents|General\\.Clip2D|Mesh\\.NbPartitions|Wire|View\\.LightTwoSide|Surface|translate|Mesh\\.CharacteristicLengthFromCurvature|General\\.SmallAxesSize|View\\.GeneralizedRaiseX|setCurrent|importShapesNativePointer|Mesh\\.Color\\.Nine|Solver\\.Executable5|getEntities|Mesh\\.Hexahedra|setAsBoundaryLayer|General\\.AxesTicsZ|ENABLE_GMP|BooleanIntersection|General\\.Clip2C|getValue|Mesh\\.SwitchElementTags|Geometry\\.CopyMeshingMethod|renumberNodes|Solver\\.RemoteLogin8|View\\.ShowTime|Solver\\.Extension3|add|View\\.Attributes|Solver\\.Timeout|RenumberMeshNodes|EndIf|General\\.PolygonOffsetUnits|Coherence Mesh|Print\\.GifDither|General\\.MinY|getElementFaceNodes|Solver\\.SocketName|ENABLE_TCMALLOC|Surface Loop|General\\.ColorScheme|Mesh\\.LabelType|General\\.SaveOptions|General\\.ZoomFactor|PostProcessing\\.SaveMesh|General\\.ClipPositionX|Mesh\\.MedSingleModel|ENABLE_MESH|Print\\.DeleteTemporaryFiles|Recombine Surface|View\\.Max|Mesh\\.Color\\.Normals|Print\\.EpsPointSizeFactor|Geometry\\.Color\\.Selection|Mesh\\.Color\\.Sixteen|General\\.MessageFontSize|Mesh\\.SmoothNormals|revolve|View\\.ArrowSizeMax|getEntitiesForPhysicalGroup|Solver\\.Name9|Geometry\\.AutoCoherence|healShapes|Mesh\\.AngleSmoothNormals|General\\.PolygonOffsetAlwaysOn|General\\.AxesTicsY|Mesh\\.MinimumCurvePoints|Background Mesh View|Print\\.EpsLineWidthFactor|ENABLE_QUADTRI|Mesh\\.OptimizeNetgen|View\\.TransformZZ|View\\.AxesLabelX|View\\.Color\\.Prisms|ENABLE_PARSER|Mesh\\.SaveParametric|ENABLE_OCC_CAF|Mesh\\.UnvStrictFormat|General\\.OptionsFileName|addWire|Mesh\\.VolumeNumbers|addModelData|General\\.GraphicsFontEngine|General\\.MouseHoverMeshes|Geometry\\.OCCParallel|General\\.Clip3A|combine|dilate|General\\.ExtraWidth|General\\.Light4|Geometry\\.Color\\.HighlightOne|General\\.AxesFormatY|General\\.ExtraPositionX|Mesh\\.PartitionCreateTopology|Mesh\\.PartitionPrismWeight|View\\.AxesTicsX|View\\.ComponentMap4|View\\.DrawHexahedra|Bezier|Geometry\\.SurfaceType|PostProcessing\\.DoubleClickedGraphPointX|Solver\\.Extension9|View\\.ComponentMap1|addThruSections|Mesh\\.CgnsImportOrder|Print\\.Text|setRecombine|View\\.OffsetZ|Solver\\.AutoArchiveOutputFiles|General\\.HighOrderToolsPositionY|Solver\\.AutoMesh|Mesh\\.LineWidth|Geometry\\.VolumeNumbers|General\\.ArrowStemLength|View\\.UseGeneralizedRaise|General\\.MaxY|addListData|Solver\\.RemoteLogin1|Geometry\\.DoubleClickedSurfaceCommand|getElementProperties|Mesh\\.PartitionTetWeight|Mesh\\.MetisMaxLoadImbalance|General\\.BackgroundImageWidth|General\\.FltkColorScheme|General\\.Orthographic|General\\.ScaleX|Mesh\\.LcIntegrationPrecision|General\\.GraphicsFontTitle|General\\.TmpFileName|ENABLE_PETSC4PY|General\\.GraphicsFont|getElementByCoordinates|Periodic Curve | Surface|awake|ENABLE_OSMESA|BSpline|ENABLE_CXX11|General\\.Light3Y|Ceil|Print\\.Background|ENABLE_POPPLER|Combine ElementsFromAllViews | Combine Views|Distance|Floor|ExternalProcess|Solver\\.Extension0|General\\.LineWidth|General\\.RotationCenterY|Print\\.PostElement|Geometry\\.NumSubEdges|View\\.AutoPosition|Solver\\.OctaveInterpreter|View\\.AxesMinY|getElementType|Solver\\.Executable6|Plane Surface|Mesh\\.Color\\.Eight|relocateNodes|View\\.LightLines|View\\.MinX|Mesh\\.MeshOnlyVisible|General\\.ShowMessagesOnStartup|Mesh\\.MaxNumThreads2D|General\\.NoPopup|Coherence|Geometry\\.Tangents|Mesh\\.Color\\.Lines|createTopology|General\\.Light4Y|Mesh\\.RecombineOptimizeTopology|General\\.Axes|ENABLE_DINTEGRATION|General\\.BackgroundImagePositionX|Translate|Print\\.X3dTransparency|PostProcessing\\.ForceNodeData|addWedge|getPrincipalCurvatures|Mesh|removeAllDuplicates|Sinh|Mesh\\.PartitionTriWeight|View\\.Group|Mesh\\.RandomFactor|ENABLE_OPTHOM|Mesh\\.SaveElementTagType|Mesh\\.ScalingFactor|get|stop|MathEvalAniso|General\\.ClipWholeElements|ENABLE_NETGEN|addSpline|list|Mesh\\.Color\\.Four|Mesh\\.Color\\.One|View\\.Explode|View\\.MinY|View\\.Color\\.Tetrahedra|Mesh\\.Color\\.Pyramids|ENABLE_BLOSSOM|Cohomology|Cosh|Geometry\\.Color\\.HighlightTwo|getNormal|General\\.RotationY|PostProcessing\\.Format|ClassifySurfaces|OptimizeMesh|View\\.AbscissaRangeType|CombinedBoundary|Print\\.X3dPrecision|Fillet|General\\.Clip0B|AttractorAnisoCurve|General\\.AxesAutoPosition|General\\.Light5X|getKeysForElements|Sin|View\\.Color\\.Normals|setOutwardOrientation|MathEval|View\\.MaxY|initialize|ENABLE_SLEPC|recombine|General\\.RotationCenterZ|View\\.AxesAutoPosition|addBox|setEntityName|Mesh\\.AllowSwapAngle|General\\.VisibilityPositionY|Mesh\\.Binary|Mesh\\.Recombine3DConformity|ENABLE_WRAP_PYTHON|Mesh\\.PartitionHexWeight|Mesh\\.PreserveNumberingMsh2|TransfQuadTri|View\\.ShowElement|synchronize|View\\.CustomMax|General\\.FieldPositionY|General\\.TrackballQuaternion1|Geometry\\.OCCBooleanPreserveNumbering|getCurvature|General\\.InitialModule|precomputeBasisFunctions|General\\.AxesValueMaxX|General\\.Light3Z|Solver\\.AutoCheck|Print\\.GeoLabels|PostProcessing\\.GraphPointX|ENABLE_ANN|Solver\\.RemoteLogin3|addElementsByType|General\\.Color\\.DiffuseLight|update|View\\.DrawPyramids|View\\.OffsetX|General\\.AxesValueMaxY|Mesh\\.SaveAll|Tanh|If|General\\.Light2W|General\\.ManipulatorPositionX|General\\.ShowOptionsOnStartup|ENABLE_C99|Mesh\\.CompoundClassify|ENABLE_OCC_TBB|BooleanUnion|General\\.InputScrolling|View\\.Stipple0|General\\.TranslationX|getEntityName|View\\.RaiseY|Physical Volume|Boundary|Mesh\\.NbTetrahedra|Solver\\.RemoteLogin6|Mesh\\.Clip|General\\.MouseInvertZoom|Geometry\\.HighlightOrphans|Geometry\\.OldNewReg|Mesh\\.RandomFactor3D|addPlaneSurface|General\\.DisplayBorderFactor|View\\.Axes|EndFor|General\\.Light3X|Solver\\.PythonInterpreter|View\\.GeneralizedRaiseZ|General\\.TrackballQuaternion3|setVisibility|ENABLE_BAMG|Mesh\\.SaveGroupsOfNodes|Mesh\\.SecondOrderLinear|getBasisFunctionsForElements|Geometry\\.MatchMeshScaleFactor|write|Ruled ThruSections|General\\.MenuPositionX|Else|Mesh\\.RadiusSup|For|removeDuplicateNodes|PostProcessing\\.DoubleClickedGraphPointY|affineTransform|Solver\\.Extension6|Mesh\\.AnisoMax|View\\.Closed|General\\.Light1Z|General\\.FieldHeight|addThickSolid|setString|getPhysicalName|General\\.RecentFile7|General\\.TrackballHyperbolicSheet|PostProcessing\\.NbViews|General\\.GraphicsFontSizeTitle|Geometry\\.Color\\.Volumes|generate|Laplacian|Mesh\\.SecondOrderExperimental|General\\.ClipOnlyDrawIntersectingVolume|General\\.PluginWidth|Mesh\\.CharacteristicLengthExtendFromBoundary|General\\.RotationX|Delete View|View\\.LineWidth|Print\\.PgfTwoDim|View\\.Color\\.Text3D|BooleanFragments|General\\.Light0X|chamfer|addSurfaceFilling|getElementsByType|Mesh\\.Color\\.Quadrangles|ReorientMesh Volume|View\\.ColormapBeta|General\\.FileChooserPositionY|Geometry\\.Clip|ENABLE_NATIVE_FILE_CHOOSER|addAlias|General\\.SmallAxesPositionX|Circle|Combine TimeStepsFromVisibleViews|Mesh\\.MetisMinConn|addDisk|getElementTypes|General\\.AxesMinX|IntersectAniso|Mesh\\.PointType|ENABLE_SOLVER|Mesh\\.LightLines|time|View\\.DoubleClickedCommand|View\\.DrawScalars|General\\.NumThreads|General\\.RecentFile5|Geometry\\.LineWidth|View\\.RaiseZ|View\\.Time|General\\.FileChooserPositionX|Mesh\\.Color\\.Five|Geometry\\.TransformXZ|View\\.CenterGlyphs|Curve Loop|View\\.DrawLines|Mesh\\.Color\\.Fourteen|Point | Curve|Solver\\.Name4|Geometry\\.ReparamOnFaceRobust|addBSpline|View\\.Stipple3|General\\.DefaultFileName|View\\.CustomAbscissaMax|General\\.Clip5C|View\\.Color\\.Trihedra|Mesh\\.Color\\.Tangents|Gradient|Mesh\\.NumSubEdges|ENABLE_MATHEX|Mesh\\.Explode|General\\.Clip4B|General\\.Clip5A|Print\\.JpegQuality|ENABLE_SYSTEM_CONTRIB|Mesh\\.QualitySup|getPartitions)\b',Keyword.Type),
            (r'(General\\.BackgroundGradient|Geometry\\.SnapY|Mesh\\.Color\\.Fifteen|Mesh\\.RecombineAll|PostProcessing\\.GraphPointY|General\\.NonModalWindows|setSize|smooth|View\\.Clip|View\\.Normals|Mesh\\.RefineSteps|General\\.MaxX|General\\.RecentFile4|View\\.CustomAbscissaMin|Transfinite Volume|getPhysicalGroupsForEntity|View\\.AxesTicsZ|Mesh\\.HighOrderPeriodic|Solver\\.Extension7|View\\.FakeTransparency|General\\.Light2Z|View\\.CustomMin|View\\.PositionX|setAsBackgroundMesh|Geometry\\.DoubleClickedEntityTag|PostProcessing\\.Smoothing|View\\.AdaptVisualizationGrid|CreateGeometry|View\\.Stipple6|Print\\.ParameterLast|View\\.Format|Geometry\\.TransformYZ|Solver\\.RemoteLogin9|Mesh\\.PartitionTrihedronWeight|symmetrize|Geometry\\.OCCDisableSTL|removeEmbedded|PostProcessing\\.DoubleClickedGraphPointCommand|Solver\\.Executable1|View\\.Stipple1|Mesh\\.Format|ENABLE_REVOROPT|Mesh\\.Color\\.Seven|Wedge|ENABLE_ONELAB|General\\.AxesMinY|Mesh\\.DrawSkinOnly|Mesh\\.RecombinationAlgorithm|Geometry\\.Lines|LonLat|Solver\\.Name6|Geometry\\.DoubleClickedPointCommand|Hide|Mesh\\.CharacteristicLengthFactor|Atan|General\\.BuildOptions|Mesh\\.Color\\.Trihedra|Mesh\\.Color\\.PointsSup|Mesh\\.Optimize|Attractor|MaxEigenHessian|View\\.Color\\.Axes|Log10|Print\\.EpsCompress|ENABLE_VOROPP|ENABLE_DOMHEX|General\\.Light0Y|open|General\\.Light5W|Geometry\\.LineSelectWidth|Print\\.EpsBestRoot|View\\.ForceNumComponents|Solver\\.AlwaysListen|View\\.AxesMaxZ|Geometry\\.OffsetX|General\\.GraphicsHeight|reorderElements|ENABLE_POST|General\\.PluginPositionY|Delete Embedded|Torus|View\\.Stipple|General\\.Clip4C|Mesh\\.Pyramids|Solver\\.RemoteLogin5|getElementEdgeNodes|PostProcessing\\.AnimationStep|General\\.OptionsPositionY|View\\.GeneralizedRaiseY|Mesh\\.Color\\.Hexahedra|ENABLE_ACIS|General\\.AlphaBlending|ENABLE_BUILD_IOS|addEllipse|Geometry\\.OCCImportLabels|ENABLE_OS_SPECIFIC_INSTALL|Mesh\\.MshFileVersion|selectViews|Mesh\\.ColorCarousel|Restrict|General\\.MinX|View\\.AxesLabelZ|Geometry\\.Volumes|getLastNodeError|getDimension|getLastEntityError|Mesh\\.NbTrihedra|Mesh\\.Prisms|General\\.Light4Z|Solver\\.Executable7|ElseIf|Solver\\.Executable8|Geometry\\.LineNumbers|Geometry\\.Color\\.HighlightZero|Mesh\\.Color\\.Eighteen|removeEntities|setNumbers|View\\.ComponentMap8|General\\.Clip1A|ENABLE_BUILD_LIB|Mesh\\.HighOrderNumLayers|View\\.Stipple2|PostProcessing\\.GraphPointCommand|General\\.Tooltips|Solver\\.Extension8|General\\.TranslationZ|Curvature|Periodic Surface|getString|addCircleArc|Mesh\\.PartitionSplitMeshFiles|View\\.AxesFormatY|Mesh\\.Color\\.Three|getBasisFunctions|View\\.TransformXZ|General\\.AxesMinZ|General\\.HighResolutionPointSizeFactor|View\\.DrawSkinOnly|View\\.Width|removePhysicalName|General\\.MinZ|Disk|getNumber|Mesh\\.BdfFieldFormat|Mesh\\.MedFileMinorVersion|PostProcessing\\.SaveInterpolationMatrices|setTransfiniteCurve|Solver\\.Extension4|View\\.ColormapAlpha|Box|ENABLE_BUILD_ANDROID|General\\.MenuPositionY|Print\\.Width|General\\.CameraEyeSeparationRatio|Fmod|Modulo|Solver\\.RemoteLogin7|Macro|reclassifyNodes|View\\.ComponentMap7|View\\.DrawTetrahedra|View\\.AxesFormatX|RenumberMeshElements|General\\.AxesValueMinZ|Plugin|View\\.Stipple7|View\\.ExternalView|Solver\\.AutoLoadDatabase|Transfinite Curve|General\\.BackgroundImagePage|General\\.ArrowHeadRadius|General\\.SmallAxes|getIndex|rebuildNodeCache|AutomaticMeshSizeField|ENABLE_ZIPPER|Ball|Frustum|General\\.SystemMenuBar|General\\.Light1Y|Print\\.PostGamma|start|Transfinite Surface|Mesh\\.ZoneDefinition|addPhysicalGroup|Mesh\\.Color\\.Points|Max|View\\.ColorTable|Cos|addRectangle|General\\.Clip0A|General\\.ShowModuleMenu|Spline|General\\.BackgroundImagePositionY|View\\.NbTimeStep|General\\.Light0|General\\.DoubleBuffer|General\\.ScaleZ|View\\.ColormapSwap|General\\.GraphicsWidth|Mesh\\.BoundaryLayerFanPoints|Mesh\\.Color\\.Twelve|Mesh\\.NbNodes|General\\.Clip1D|getNodesByElementType|Mesh\\.Lines|View\\.Stipple5|General\\.RotationCenterX|View\\.Color\\.Background2D|Print\\.Format|View\\.AxesMikado|General\\.Light4X|General\\.TextEditor|Mesh\\.PartitionPyramidWeight|General\\.DrawBoundingBoxes|General\\.RecentFile3|View\\.AxesMaxY|General\\.FontSize|Geometry\\.OffsetZ|View\\.MaxX|General\\.Light4W|View|Mean|Print\\.GifInterlace|getGhostElements|getNodes|Print\\.X3dCompatibility|Geometry\\.OldRuledSurface|Solver\\.AutoShowLastStep|General\\.Clip0C|computeHomology|View\\.Height|General\\.RotationZ|General\\.ShininessExponent|General\\.ExecutableFileName|Print\\.EpsOcclusionCulling|embed|Mesh\\.PartitionOldStyleMsh2|Mesh\\.Quadrangles|View\\.ColormapRotation|General\\.Color\\.SpecularLight|addCylinder|General\\.SessionFileName|getInformationForElements|Mesh\\.MetisEdgeMatching|optimize|General\\.Color\\.SmallAxes|Mesh\\.QualityType|View\\.GlyphLocation|Point | Curve | Surface|setTransfiniteVolume|Mesh\\.SurfaceEdges|View\\.AxesTicsY|addCurveLoop|PostView|Geometry\\.Points|General\\.Color\\.Axes|Mesh\\.Color\\.Seventeen|General\\.PluginPositionX|View\\.TransformYZ|Mesh\\.HighOrderThresholdMin|View\\.Color\\.Points|preallocateElementsByType|Mesh\\.StlRemoveDuplicateTriangles|View\\.PointSize|View\\.AngleSmoothNormals|View\\.DrawStrings|ENABLE_GRAPHICS|Solver\\.Plugins|Mesh\\.SubdivisionAlgorithm|Solver\\.Name3|Mesh\\.Color\\.Ten|Mesh\\.HighOrderPassMax|ENABLE_GETDP|Geometry\\.OrientedPhysicals|Geometry\\.MatchGeomAndMesh|Fabs|addVolume|setSmoothing|ENABLE_CAIRO|General\\.MouseSelection|Geometry\\.MatchMeshTolerance|splitQuadrangles|Mesh\\.Color\\.Nineteen|Geometry\\.TransformZZ|View\\.DrawPrisms|getElements|General\\.Terminal|getListData|Atan2|twist|General\\.GraphicsPositionY|Geometry\\.TransformXX|Line|CopyOptions View|General\\.GraphicsFontSize|Geometry\\.OCCFixSmallFaces|General\\.Light3W|Mesh\\.HighOrderOptimize|Mesh\\.Voronoi|General\\.Light0W|Geometry\\.OCCTargetUnit|Solver\\.Extension5|View\\.PositionY|View\\.Min|View\\.VectorType|ENABLE_MSVC_STATIC_RUNTIME|View\\.TransformZY|Mesh\\.Algorithm|General\\.ClipPositionY|Mesh\\.Color\\.Thirteen|General\\.Light3|View\\.MaxZ|General\\.Color\\.Text|Mesh\\.Color\\.Six|Rand|Mesh\\.Color\\.Zero|General\\.AxesMaxY|RelocateMesh Point | Curve | Surface|Mesh\\.Color\\.Two|ENABLE_ONELAB_METAMODEL|General\\.AxesLabelZ|Mesh\\.ToleranceInitialDelaunay|addSurfaceLoop|Geometry\\.Surfaces|Mesh\\.SurfaceFaces|General\\.Light2|View\\.DrawVectors|extrude|Min|ENABLE_FLTK|View\\.Name|getParent|Mesh\\.MedImportGroupsOfNodes|General\\.HighResolutionGraphics|Exp|Solver\\.Executable9|General\\.ContextPositionY|MeshAlgorithm Surface|rotate|Print\\.PostSIGE|General\\.RecentFile8|View\\.ColormapBias|selectElements|Mesh\\.Algorithm3D|PostProcessing\\.DoubleClickedView|createGeometry|General\\.DetachedMenu|Geometry\\.OCCScaling|Geometry\\.ScalingFactor|removePhysicalGroups|General\\.RotationCenterGravity|Rectangle|Solver\\.AutoSaveDatabase|copyOptions|ENABLE_3M|General\\.AxesMaxX|General\\.Color\\.Background|General\\.SmallAxesPositionY|General\\.AxesMaxZ|General\\.FieldWidth|Round|cputime|General\\.ClipFactor|Characteristic Length|remove|View\\.ComponentMap6|Mesh\\.Tetrahedra|ENABLE_VISUDEV|fragment|Field|View\\.ScaleType|View\\.PointType|removeEntityName|Geometry\\.OCCAutoFix|General\\.Verbosity|Geometry\\.TransformXY|ENABLE_MMG3D|PostProcessing\\.AnimationCycle|Mesh\\.NewtonConvergenceTestXYZ|General\\.Light1X|Mesh\\.IgnorePeriodicity|setColor|getBoundingBox|Mesh\\.CpuTime|General\\.Clip3C|Mesh\\.SaveTopology|Mesh\\.Tangents|Print\\.ParameterSteps|getNodesForPhysicalGroup|General\\.RecentFile1|General\\.VisibilityPositionX|getNode|classifySurfaces|General\\.BoundingBoxSize|ENABLE_MUMPS|ENABLE_OCC|ENABLE_OCC_STATIC|General\\.Clip2A|General\\.Clip3D|General\\.Clip5D|General\\.BackgroundImageHeight|Geometry\\.Tolerance|Print\\.EpsQuality|General\\.ConfirmOverwrite|Hypot|Mesh\\.SmoothCrossField|View\\.ComponentMap2|Solver\\.Extension2|View\\.MinZ|Print\\.GifTransparent|Geometry\\.DoubleClickedLineCommand|Mesh\\.Color\\.Eleven|Mesh\\.Trihedra|View\\.RaiseX|Mesh\\.OptimizeThreshold|View\\.AxesMaxX|Solver\\.Name0|Mesh\\.NbQuadrangles|Print\\.PgfHorizontalBar|Print\\.PostEta|addElements|Mesh\\.HighOrderPrimSurfMesh|finalize|Mesh\\.HighOrderThresholdMax|View\\.TargetError|refine|Sqrt|Geometry\\.OCCFixSmallEdges|fuse|Physical Point|General\\.Display|Mesh\\.Normals|renumberElements|View\\.TransformXY|Mesh\\.VolumeFaces|Print\\.X3dRemoveInnerBorders|ThruSections|Print\\.CompositeWindows|preallocateBarycenters|PostProcessing\\.Link|MinAniso|View\\.NormalRaise|General\\.AxesValueMinX|ENABLE_BUILD_SHARED|View\\.ComponentMap0|Mesh\\.Points|Compound Curve | Surface|setPhysicalName|getIntegrationPoints|ENABLE_WRAP_JAVA)\b',Keyword.Type),
            (r'(class)(\s+)', bygroups(Keyword, Text), 'classname'),
            # C++11 raw strings
            (r'(R)(")([^\\()\s]{,16})(\()((?:.|\n)*?)(\)\3)(")',
             bygroups(String.Affix, String, String.Delimiter, String.Delimiter,
                      String, String.Delimiter, String)),
            # C++11 UTF-8/16/32 strings
            (r'(u8|u|U)(")', bygroups(String.Affix, String), 'string'),
            inherit,
        ],
        'root': [
            inherit,
            # C++ Microsoft-isms
            (words(('virtual_inheritance', 'uuidof', 'super', 'single_inheritance',
                    'multiple_inheritance', 'interface', 'event','ascii'),
                   prefix=r'__', suffix=r'\b'), Keyword.Reserved),
            # Offload C++ extensions, http://offload.codeplay.com/
            (r'__(offload|blockingoffload|outer)\b', Keyword.Pseudo),
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop'),
            # template specification
            (r'\s*(?=>)', Text, '#pop'),
        ],
    }

    def analyse_text(text):
        if re.search('#include <[a-z_]+>', text):
            return 0.2
        if re.search('using namespace ', text):
            return 0.4
        if re.search('type ', text):
            return 0.4
        if re.search('value ', text):
            return 0.4
