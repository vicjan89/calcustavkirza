# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
author_index = 0
chapter = 'Расчет уставок РЗА сети 33 кВ'
copyright = '2024, ООО Электротехнические решения'
author = ('ООО Электротехнические решения', 'ООО "МигТехноСтрой"')[author_index]
release = '0.1'
project_code = 'СЕАВ.23190-РР'
state = (('А', 'Архитектурный проект'), ('С', 'Строительный проект'))[1]
pris = (('zapadnaja', 'Реконструкция подстанции 110/35/10 кВ «Западная» по ул. Тимирязева, 60', '23.10.2023'),
        ('source_data_rp_vodozabor_kommunalniy', 'ЦЭО. Модернизация системы электроснабжения 10кВ водозабора "Коммунальный"', '23.01.2024'),
        ('source_data_tp_from_gurgevo', 'Возведение рыбоперерабатывающего предприятия на территории СЭЗ "Витебск" по ул.'
                                        ' 1-я Журжевская в г.Витебске', '19.02.2024'),
        ('pech_kovsh', 'Модернизация системы высоковольтного распределения электроэнергии печи-ковша LF-4 в ЭСПЦ-2',
         '07.05.2024'))
num = 3
today = pris[num][2]
project = pris[num][1]
root_doc = pris[num][0]
utverdil = ('Рулинский', '')[author_index]
norma_control = ('Зайцев', '')[author_index]
proveril = ('Юроца', '')[author_index]
razrabotal = ('Януш', '')[author_index]


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
#-- Options for LaTeX output -------------------------------------------------
latex_maketitle = []
latex_maketitle.append(r'\begin{titlepage}')
if author_index == 0:
    latex_maketitle.append(r'\AddToShipoutPicture*{\put(500,755){\includegraphics{QR}}}')
latex_maketitle.append(r'\begin{center}')
latex_maketitle.append(r'{\Large ' + author + r'\par')
latex_maketitle.append(r'\vspace{30mm}')
latex_maketitle.append(r'{\bfseries ' + project + r'\par')
latex_maketitle.append(r'\vspace{4cm}')
latex_maketitle.append(state[1] + r'\par')
latex_maketitle.append(r'\vspace{15mm}')
latex_maketitle.append(chapter + r'\par}}')
latex_maketitle.append(r'\vspace{30mm}')
latex_maketitle.append(r'{\large {\bfseries ' + project_code + r'}\par}')
latex_maketitle.append(r'\vspace{30mm}')
latex_maketitle.append(r'\end{center}')
if author_index == 0:
    latex_maketitle.append(r'{\large Заместитель главного инженера \hspace{35mm} Директор\\')
    latex_maketitle.append(r'\rule{30mm}{0.4px}В.А.Рулинский \hspace{40mm} \rule{30mm}{0.4px}В.С.Карпук\\')
    latex_maketitle.append(r'\\')
    latex_maketitle.append(r'Главный инженер проекта\\')
    latex_maketitle.append(r'\rule{30mm}{0.4px}В.А.Ильянок}')
latex_maketitle.append(r'\begin{center}')
spc = 20 if author_index == 0 else 50
latex_maketitle.append(r'\vspace{' + str(spc) +'mm}')
latex_maketitle.append(r'{\small Минск,2024}' if author_index == 0 else r'{\small Витебск,2024}')
latex_maketitle.append(r'''\end{center}
\newpage
\quad
\AddToShipoutPicture{\BackgroundPicture}
\end{titlepage}
''')
latex_maketitle = '\n'.join(latex_maketitle)
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '12pt',
    # Additional stuff for the LaTeX preamble.
    'maketitle': latex_maketitle,
    # Latex figure (float) alignment
    'figure_align': 'H', # htbp - default ,при H рисунки располагаются в том месте где указано, не плавают на другие страницы
    'extraclassoptions': 'openany', #'manual',
    'preamble': r'''
% создание рамки на каждой странице
\usepackage{eso-pic,graphicx}
\usepackage{lastpage}
\makeatletter

\newcommand\BackgroundPicture{%
  \setlength{\unitlength}{1pt}%
  \put(0,\strip@pt\paperheight){%
  \parbox[t][\paperheight]{\paperwidth}{%
    \vfill
    \ifnum \value{page}=2
        \centering\includegraphics[angle=0]{A4l2}
    \else
        \ifnum \value{page}=3 {%
            \centering\includegraphics[angle=0]{A4l3}}
        \else {%
            \centering\includegraphics[angle=0]{A4l4}}
        \fi
    \fi
    \vfill
}}%
    \ifnum \value{page}=3 
        \put(350, 100){\Large ''' + project_code + r'''}
        \put(460, 60){\normalsize ''' + state[0] + r'''\hspace{55px} 3 \hspace{40px} \pageref{LastPage}}
        \put(115, 60){''' + utverdil + r'''}
        \put(115, 45){''' + norma_control + r'''}
        \put(115, 30){''' + proveril + r'''}
        \put(115, 17){''' + razrabotal + r'''}
        \put(60, 60){Утвердил}
        \put(230, 50){\parbox{8cm}{\centering {\large ''' + chapter + r'''}}}
    \else 
        \ifnum \value{page}>3
            \put(330,30){\Large ''' + project_code + r''' }
        \fi
    \fi
}%


\renewcommand{\sphinxtableofcontents}{%
  \begingroup
    \parskip \z@skip
    \sphinxtableofcontentshook
    \tableofcontents
  \endgroup
  \vspace{12pt}%
}

\makeatother
% делаем первую страницу оглавления чуть короче чтобы влезть в рамку
\renewcommand\sphinxtableofcontentshook{\enlargethispage{-80px}}
\renewcommand{\headrulewidth}{0pt}
\setlength{\headsep}{-20pt} % уменьшаем верхнее поле
\setlength{\footskip}{1pt} % уменьшаем нижнее поле
\setlength{\textheight}{750pt} % уменьшаем высоту текста
% перенос номера страниц
\usepackage{fancyhdr}
\fancypagestyle{normal}{\fancyhf{} \fancyfoot[R]{\put(37,-32){\thepage}}} %% страницы внизу - вправо
\fancypagestyle{plain}{\fancyhf{} \fancyfoot[R]{\put(-15, -90){\thepage}}} %% страницы внизу - вправо
'''
}

engines = ('pdflatex', 'xelatex', 'lualatex', 'platex', 'uplatex')
latex_engine = engines[2]
# Grouping the document tree into LaTeX files. List of tuples
# (source_old start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
theme = ('manual', 'howto')[1]
latex_documents = [
    (root_doc, pris[num][0]+'.tex', pris[num][1], 'ООО Электротехнические Решения', theme),
]
latex_table_style = ['standart']

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#
latex_logo = '_static/ER.png'

# If true, show page references after internal links.
#
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
#
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
#
# latex_appendices = []

# If false, no module index is generated.
#
# latex_domain_indices = True
