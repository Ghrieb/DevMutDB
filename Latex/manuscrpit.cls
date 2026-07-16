%% ERTS LaTeX Class
%% Based on standard LaTeX article class and PHM Society LaTeX Class


% Class setup
\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{ERTS}[2025/03/17 v0.02 ERTS LaTeX Class]
\LoadClassWithOptions{article}

% ------------------------------------------------------------------------------------------
%
%: PACKAGE REQUIREMENTS
%
% ------------------------------------------------------------------------------------------
\RequirePackage{times}						% font selection
\RequirePackage{fancyhdr}					% for headers/footers
\RequirePackage{flushend}					% evening out final page
\RequirePackage[labelsep=period, format=plain]{caption}
\RequirePackage[hang,flushmargin]{footmisc} % for footnotes
\RequirePackage[square,numbers]{natbib}
% \RequirePackage[natbibapa]{apacite}				% for citation style, see https://ctan.math.illinois.edu/macros/latex/contrib/apacite/apacite.pdf
\RequirePackage[english]{babel}		% for apacite setup
\RequirePackage{setspace}					% to enforce single spacing of bibliography
\RequirePackage[a4paper, right=1.5cm, left=1.5cm, top=2cm, bottom=2cm]{geometry}
\RequirePackage{draftwatermark}         % for DRAFT option

% ------------------------------------------------------------------------------------------
%
%: PAGE LAYOUT
%
% ------------------------------------------------------------------------------------------
\twocolumn  								% two column paper
\setlength\columnsep{6.4mm}                                             % space between columns
\flushbottom 								% 



% -- Header and top margins
% NOTE: The top margin assume that the origin is at 1" (\voffset) to the top of the header box
% Check for reference: http://help-csli.stanford.edu/tex/latex-margins.shtml
%\setlength\topmargin{-0.5in}			% Move up to accommodate header box
%\setlength\headheight{0.15in} 			% Header box is 0.5in hight
%\setlength\headsep{0.35in}

% --- Title box setup
\newlength\titlebox 					% define new length variable
\setlength\titlebox{3.5in}				% This is a default value only, it might need to be modified in the *.tex file to 
								% account for cases with more affiliations and authors that will require a 
								% bigger box

% To do activities:
% - The "titlebox" work needs user input for cases with extended number of authors. Consider modifying this infrastructure so it is done automatically without the user modifying the "\titlebox" in the *.tex file
% END of PAGE LAYOUT Configuration


% ------------------------------------------------------------------------------------------
%
%: HEADER AND FOOTER CONTENT DECLARATIONS
%
% ------------------------------------------------------------------------------------------

% no header/footer for first page
\thispagestyle{empty}
\pagestyle{fancy}
\fancyhead{}
\fancyfoot{}

% set up publication year, which may be given as an option
\def\publicationYear{20xx}

\DeclareOption{2026}{
\def\publicationYear{2026}
}

\DeclareOption{2028}{
\def\publicationYear{2028}
}

\DeclareOption{2030}{
\def\publicationYear{2030}
}

\DeclareOption{2032}{
\def\publicationYear{2032}
}

\DeclareOption{2034}{
\def\publicationYear{2034}
}

\DeclareOption{2036}{
\def\publicationYear{2036}
}


% set up correct header based on publication

\DeclareOption{DRAFT}{%
  \SetWatermarkScale{1}
  \fancyhead[C]{\small{\textsc{Draft version}}}%
  \renewcommand{\headrulewidth}{0pt} % Remove head ruler
  \fancyfoot[R]{{\small{\thepage}}}  % --- footer all pages
  \fancypagestyle{plain}{            % --- first page header and footer content
    \fancyhead[C]{}                  % --- Clear first page header
    \fancyfoot[L]{\small{ERTS~DRAFT~DRAFT~DRAFT}}%	% --- Write first page footer
  }
}

\DeclareOption{ERTS}{%
  \DraftwatermarkOptions{nostamp}       % Does no print DRAFT
  \fancyhead[C]{\small{\textsc }}% Title on all pages top center
  \renewcommand{\headrulewidth}{0pt}	% Remove head ruler
  \fancyfoot[R]{{\small{\thepage}}}     % --- footer all pages
  \fancypagestyle{plain}{               % --- first page header and footer content
  \fancyhead[C]{}}                      % --- Clear first page header
  \fancyfoot[L]{\small{ }}%	% --- Write first page footer
}

\ProcessOptions\relax

% END OF HEADER AND FOOTER CONTENT DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: FONT SIZE DECLARATIONS
%
% ------------------------------------------------------------------------------------------
% http://wiki.lyx.org/FAQ/ChangeFontUsingLatex
% http://xpt.sourceforge.net/techdocs/language/latex/latex32-LaTeXAndFonts/ar01s14.html
\def\@normalsize{\@setsize\normalsize{10pt}\xpt\@xpt}   		% 10 point on 11
\def\normalsize{\@setsize\normalsize{10pt}\xpt\@xpt}   		% 10 point on 11
\def\small{\@setsize\small{9pt}\ixpt\@ixpt}            			% 9 point on 10
\def\footnotesize{\@setsize\footnotesize{8pt}\viiipt\@viiipt} 	% 9 point on 10
\def\scriptsize{\@setsize\scriptsize{8pt}\viiipt\@viiipt} 		% 7 point on 8
\def\tiny{\@setsize\tiny{7pt}\viipt\@viipt}               			% 6 point on 7
\def\large{\@setsize\large{12pt}\xiipt\@xiipt}            			% 11 point on 12
\def\Large{\@setsize\Large{14pt}\xivpt\@xivpt}          		% 12 point on 14
\def\LARGE{\@setsize\LARGE{16pt}\xviipt\@xviipt}          		% 14 point on 16
\def\huge{\@setsize\huge{18pt}\xviiipt\@xviiipt}          		% 17 point on 20
\def\Huge{\@setsize\Huge{23pt}\xxiiipt\@xxiiipt}              		% 20 point on 23
\def\email{\@setsize\email{9pt}\ixpt\@ixpt}              			% 9 point
% TO DO:
% - This needs to be properly configured and documented. There might not be a need to do this.
% - Look at the article.cls class to identify how the sizes are defined. There should be a file size10.clo that will contain
%   the standard definitions.
% END of FONT SIZE DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: PARAGRAPH DECLARATIONS
%
% ------------------------------------------------------------------------------------------
% Linespacing
% NOTE: Use \linespread{1.3} for "one and a half" line spacing, and \linespread{1.6} for "double" line spacing.
\linespread{1.2}
% [MD] setspace package might be easier to use?

% Indentation
\setlength{\parindent}{0pt}

% Spacing between paragraphs
\setlength{\parskip}{6pt}

% NOTES
% - \parskip will affect lists too. This needs to be fixed later on the lists environments
% END of PARAGRAPH DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: TITLE BLOCK DECLARATIONS
%
% ------------------------------------------------------------------------------------------
\def\@maketitle{%
	\def\and{\unskip{, }}
  	\def\And{\unskip{, and }}
	\vskip 0.55in 										% Space before title is 0.5"
	\begin{center}
		{\LARGE\bf\@title\par}					% Title text
		%
		\vskip 14pt											% Space after title, 14pt
		%
		{\normalsize \@author \par}			% Author text			
		%
		\vskip 0.02in										% Space after authors, 12pt
		%
		{\normalsize\it									% Affiliation
		\vskip -1pt
		\begin{tabular}[t]{c}				
			\address
		\end{tabular}
		\par}
		%
		\vskip 26pt											% Space after affiliation, 24 + 3 pt
		%
	\end{center}
} % end maketitle definition

% END of TITLE BLOCK DECLARATIONS

% ------------------------------------------------------------------------------------------
%
%: ABSTRACT ENVIRONMENT DECLARATIONS
%
% ------------------------------------------------------------------------------------------
\renewenvironment{abstract}{\centerline{\normalsize\bfseries\scshape Abstract}\vspace{0pt}\noindent\normalsize}
% NOTE
% - No need to remove vspace because the \parskip variable is set to 6pt. If this variable is changed, then this needs to be updated.
% END of ABSTRACT ENVIRONMENT DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: LICENSE FOOTNOTE DECLARATIONS
%
% ------------------------------------------------------------------------------------------
\newcommand{\licenseFootnote}[1]{%
  \insert\footins{\noindent\footnotesize{#1. This is an open-access article distributed under the terms of
     the Creative Commons Attribution 4.0 License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.}}
}
% TO DO:
% - Make use of a variable for the first name. This way the author will have to provide it only once
% END of LICENSE FOOTNOTE DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: AFFILIATIONS DECLARATIONS
%
% ------------------------------------------------------------------------------------------
\newcommand{\authorNumber}[1]{\textnormal{\textsuperscript{#1}}}	 	% This command is for formatting the author 
														% number as a subscript
\newcommand{\affiliation}[3]{\\ \authorNumber{#1} #2 \\ #3}
\newcommand{\address}[1]{\def\address{#1}}

% TO DO:
% - Consider changing the structure of this so authors cannot mess up layout of affiliation section
%END of AFFILIATIONS DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: SECTIONS DECLARATIONS
%
% ------------------------------------------------------------------------------------------

% Section font style and before/after spacing   
\def\section{\@startsection{section}{1}{\z@}{6pt}{0.01pt}{\normalsize\bf\scshape}}
\def\subsection{\@startsection{subsection}{2}{\z@}{6pt}{0.01pt}{\normalsize\bf}}
\def\subsubsection{\@startsection{subsubsection}{3}{\z@}{6pt}{0.01pt}{\normalsize\bf}}

% NOTE: Argument for definition as stated on the IEEE templates. Not sure if correct.
% arguments are: #1 - sectiontype name
% (for \@sect)   #2 - section level
%                #3 - section heading indent
%                #4 - top separation (absolute value used, neg indicates not to indent main text)
%                     If negative, make stretch parts negative too!
%                #5 - (absolute value used) positive: bottom separation after heading,
%                      negative: amount to indent main text after heading
%                Both #4 and #5 negative means to indent main text and use negative top separation
%                #6 - font control
% You've got to have \normalfont\normalsize in the font specs below to prevent

% \@startsection {NAME}{LEVEL}{INDENT}{BEFORESKIP}{AFTERSKIP}{STYLE} 
%            optional * [ALTHEADING]{HEADING}
%    Generic command to start a section.  
%    NAME       : e.g., 'subsection'
%    LEVEL      : a number, denoting depth of section -- e.g., chapter=1,
%                 section = 2, etc.  A section number will be printed if
%                 and only if LEVEL < or = the value of the secnumdepth
%                 counter.
%    INDENT     : Indentation of heading from left margin
%    BEFORESKIP : Absolute value = skip to leave above the heading.  
%                 If negative, then paragraph indent of text following 
%                 heading is suppressed.
%    AFTERSKIP  : if positive, then skip to leave below heading,
%                       else - skip to leave to right of run-in heading.
%    STYLE      : commands to set style
%  If '*' missing, then increments the counter.  If it is present, then
%  there should be no [ALTHEADING] argument.  A sectioning command
%  is normally defined to \@startsection + its first six arguments.
%
% \z@ is shorthand for 0pt indentation from left margin


% Define section numbering styles
\def\thesection{\arabic{section}}
\def\thesubsection{\thesection.\arabic{subsection}}
\def\thesubsubsection{\thesubsection.\arabic{subsubsection}}

%% Singlespace References
\newcommand{\PHMbibliography}[1]{\begin{singlespace}\bibliography{#1}\end{singlespace}}

% Update section formatting to include period after the section number
% to match MS word style
\renewcommand*{\@seccntformat}[1]{
       \csname the#1\endcsname.
}
% the "\csname the#1\endcsname" part puts in the section number, then the 
% "." there puts in the ".", and then the "\quad" inserts some space. 
% There is a description here:
% http://www.tex.ac.uk/cgi-bin/texfaq2html?label=seccntfmt

% NOTES on Latex sections
% http://help-csli.stanford.edu/tex/latex-sections.shtml
% END of SECTIONS DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: FOOTNOTES DECLARATIONS
%
% ------------------------------------------------------------------------------------------
\footnotesep 6.65pt \skip\footins 9pt plus 4pt minus 2pt
\def\footnoterule{\kern-3pt \hrule width 5pc \kern 2.6pt }
\setcounter{footnote}{0}
% NOTE:
% TO DO:
% - Not sure if these declarations are actually needed
% END of FOOTNOTES DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: ILLUSTRATIONS DECLARATIONS
%
% ------------------------------------------------------------------------------------------
\floatsep 12pt plus 2pt minus 2pt
\textfloatsep 16pt plus 2pt minus 4pt
\intextsep 12pt plus 2pt minus 2pt
\dblfloatsep 12pt plus 2pt minus 2pt
\dbltextfloatsep 18pt plus 2pt minus 4pt
% NOTE:
% TO DO:
% - Not sure if these declarations are actually needed
% END of ILLUSTRATIONS DECLARATIONS


% ------------------------------------------------------------------------------------------
%
%: DISPLAYS DECLARATIONS
%
% ------------------------------------------------------------------------------------------
\abovedisplayskip 7pt plus2pt minus5pt%
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip  0pt plus3pt%   
\belowdisplayshortskip  4pt plus3pt minus3pt%
% END of DISPLAYS DECLARATIONS



% ------------------------------------------------------------------------------------------
%
%: LISTS DECLARATIONS
%
% ------------------------------------------------------------------------------------------
% Indentation for all the lists and sublists. Applies to enumerate, itemize
\leftmargini 0.25in				% This should be 0.25in which is the column separation size
\leftmarginii 2em
\leftmarginiii 1em 
\leftmarginiv 0.5em
\leftmarginv 0.5em 
\leftmarginvi 0.5em

% Applies to enumerate, itemize and description
\leftmargin\leftmargini							% ???
\labelsep 10pt									% separation from label to text (update w/MSWord dim.)
\labelwidth\leftmargini\advance\labelwidth-\labelsep


% Applies to enumerate, itemize and description
\def\@listI{\leftmargin\leftmargini 
\parsep 0pt plus 1pt minus 0.5pt%					% This is the element to element separation
\topsep 0pt plus 1pt minus 2pt%					% this is the top separation
\itemsep 3pt plus 1pt minus 0.5pt%					% This is the element to element separation (repeated)
\partopsep 6pt plus 0.5pt minus 0.5pt}				% bottom separation

\let\@listi\@listI					% ??
\@listi 						% ??

\def\@listii{\leftmargin\leftmarginii
   \labelwidth\leftmarginii\advance\labelwidth-\labelsep
   \parsep 1pt plus 0.5pt minus 0.5pt
   \topsep 2pt plus 1pt minus 0.5pt
   \itemsep \parsep}
\def\@listiii{\leftmargin\leftmarginiii
    \labelwidth\leftmarginiii\advance\labelwidth-\labelsep
    \parsep 0pt plus 1pt
    \partopsep 0.5pt plus 0pt minus 0.5pt
    \topsep 1pt plus 0.5pt minus 0.5pt 
    \itemsep \topsep}
\def\@listiv{\leftmargin\leftmarginiv
     \labelwidth\leftmarginiv\advance\labelwidth-\labelsep}
\def\@listv{\leftmargin\leftmarginv
     \labelwidth\leftmarginv\advance\labelwidth-\labelsep}
\def\@listvi{\leftmargin\leftmarginvi
     \labelwidth\leftmarginvi\advance\labelwidth-\labelsep}
% NOTE:
% TO DO:
% - This section needs to be properly understood. Embedded lists needing indented numbering have not been tested.     
% END of LISTS DECLARATIONS



