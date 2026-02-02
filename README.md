Representações Celulares e Esfera Geodésica

Modelagem Geométrica — IMPA, Verão 2026
Prof. Luiz Henrique de Figueiredo


Sobre
Este repositório contém a implementação das duas primeiras tarefas do curso de Modelagem Geométrica do IMPA. A Tarefa 1 explora representações celulares (uniformes e adaptativas) de regiões definidas implicitamente no plano. A Tarefa 2 constrói esferas geodésicas a partir de sólidos platônicos, exportando malhas triangulares em formato OBJ.
A implementação foi feita em Python. Minha ideia inicial era usar C++, mas tive bastante dificuldade para montar o ambiente de compilação e linking com bibliotecas gráficas, então migrei para Python com matplotlib e numpy — o que acabou sendo uma boa escolha pela facilidade de iteração e visualização rápida dos resultados.

Estrutura do repositório
├── tarefa1_celular.py      # Representações celulares (uniforme + quadtree)
├── tarefa2_geodesica.py    # Esfera geodésica (subdivisão + projeção)
├── relatorio_mg.pdf        # Relatório (4 páginas)
├── apresentacao_mg.pptx    # Slides para apresentação (3 slides)
└── README.md
Ao rodar cada script, as imagens e arquivos OBJ são gerados na mesma pasta do script.

Tarefa 1 — Representações Celulares
O problema
Dada uma função implícita f(x,y)f(x,y)
f(x,y) que define uma região no plano (f≤0f \leq 0
f≤0 = dentro, f=0f = 0
f=0 = fronteira, f>0f > 0
f>0 = fora), queremos classificar subdivisões retangulares do domínio em
dentro, fora ou fronteira.
Duas formas testadas para o disco com centro (0.3,0.4)(0.3, 0.4)
(0.3,0.4) e raio 0.210.21
0.21 no quadrado unitário, e para a região y≥x2+cy \geq x^2 + c
y≥x2+c em [−2,2]2[-2, 2]^2
[−2,2]2:

Classificação via TVI
A classificação de cada célula usa o Teorema do Valor Intermediário — um resultado que vem de Bolzano (1817), muito antes de ser formalizado por Weierstrass. A ideia é elegante na sua simplicidade: se ff
f é contínua e assume valores positivos e negativos nos cantos de uma célula retangular, então necessariamente f=0f = 0
f=0 em algum ponto interior. Ou seja, a fronteira cruza a célula.

Na prática, avaliamos ff
f nos 4 cantos:


Todos ≤0\leq 0
≤0 → célula
dentro
Todos >0> 0
>0 → célula
fora
Sinais mistos → célula de fronteira

É um teste barato (4 avaliações de ff
f) e suficiente para as formas desta tarefa, embora possa falhar para curvas que entram e saem da célula sem tocar nenhum canto — nesse caso, seriam necessários oráculos intervalares, como discutido em aula.

Enumeração uniforme
Divide o domínio numa grade regular N×NN \times N
N×N. Cada célula é classificada independentemente. É o método mais simples: para 32×3232 \times 32
32×32, temos 1024 células. Funciona, mas gasta a mesma resolução em regiões que são inteiramente dentro ou inteiramente fora — onde não precisamos de detalhe nenhum.

Enumeração adaptativa (Quadtree)
A Quadtree resolve exatamente essa ineficiência. A estrutura de dados foi introduzida por Finkel e Bentley (1974) para busca em chaves compostas, mas se aplica naturalmente à enumeração espacial: começamos com uma única célula cobrindo todo o domínio e subdividimos recursivamente em 4 quadrantes apenas as células classificadas como fronteira. Células homogêneas (toda dentro ou toda fora) permanecem grandes.
O refinamento adaptativo segue a abordagem de Suffern (1990), que aplicou quadtrees especificamente para contorno de funções de duas variáveis.
Resultado para o disco: a Quadtree (profundidade máxima 7) usa 583 células contra 1024 da uniforme — 43% menos — com resolução muito superior na fronteira.
Resultados visuais
Disco — Uniforme vs. Adaptativa:
Show Image
Parábola y≥x2y \geq x^2
y≥x2 — Uniforme vs. Adaptativa:

Show Image
Evolução do refinamento adaptativo (profundidades 1 a 7):
Show Image
A evolução mostra como a Quadtree vai concentrando resolução na circunferência do disco a cada nível, mantendo células grandes nas regiões homogêneas. É visualmente satisfatório ver a fronteira emergir com precisão crescente.
Variações da parábola (c = 0, −1, 1, 0.5):
c = 0c = −1c = 1c = 0.5Show ImageShow ImageShow ImageShow Image
A Quadtree se adapta automaticamente à geometria da fronteira em todos os casos, sem nenhuma mudança de parâmetros.
Dificuldades na Tarefa 1
A maior dificuldade conceitual foi entender os limites da classificação por cantos. O TVI garante que sinais opostos implicam cruzamento, mas a recíproca não vale: a fronteira pode cruzar a célula sem que os cantos detectem (quando a curva faz uma "excursão" para dentro da célula e volta sem tocar nenhum canto). Para um disco e uma parábola isso não acontece, mas me fez pensar sobre o que seria necessário para curvas mais patológicas — e a resposta que vi nas notas do curso é usar aritmética intervalar, que dá garantias mais fortes.
Outra questão prática foi a escolha da profundidade mínima da Quadtree. Se começo com profundidade mínima 0, a raiz pode ser classificada como "dentro" para discos pequenos no centro do domínio, e o algoritmo nunca refina. Usar profundidade mínima 2 resolve isso, garantindo pelo menos 42=164^2 = 16
42=16 células antes de começar a decidir se refina ou não.


Tarefa 2 — Esfera Geodésica
O problema
Gerar uma esfera geodésica no formato Wavefront OBJ, partindo de um sólido platônico de faces triangulares. O método é: subdividir cada triângulo em 4 subtriângulos (pelos pontos médios das arestas) e projetar os novos vértices na esfera unitária por normalização.
Contexto histórico
A esfera geodésica tem uma história bonita fora da matemática. Buckminster Fuller popularizou o domo geodésico nos anos 1950 como uma estrutura arquitetônica — o domo do pavilhão americano na Expo 67 de Montreal é talvez o mais icônico. Mas a construção matemática subjacente é mais antiga: a ideia de aproximar uma esfera por subdivisão de poliedros regulares remonta ao estudo dos sólidos platônicos, que Euclides já formalizava nos Elementos (~300 a.C.).
O fato de usarmos o icosaedro como ponto de partida preferencial não é por acaso: suas 20 faces triangulares equiláteras produzem a subdivisão mais uniforme entre os sólidos platônicos, porque os triângulos iniciais são mais "parecidos entre si" do que os de um tetraedro ou octaedro.
Algoritmo de subdivisão
Para cada triângulo ABCABC
ABC:


Calcular pontos médios: D=A+B2D = \frac{A+B}{2}
D=2A+B​, E=B+C2E = \frac{B+C}{2}
E=2B+C​, F=A+C2F = \frac{A+C}{2}
F=2A+C​
Projetar na esfera: D←D∥D∥D \leftarrow \frac{D}{\|D\|}
D←∥D∥D​ (e analogamente para EE
E, FF
F)

Substituir por 4 subtriângulos: (A,D,F)(A, D, F)
(A,D,F), (D,B,E)(D, B, E)
(D,B,E), (F,E,C)(F, E, C)
(F,E,C), (D,E,F)(D, E, F)
(D,E,F)

    A                 A
   / \     →        / \
  /   \            D---F
 /     \          / \ / \
B-------C        B---E---C
A cada nível, o número de faces se multiplica por 4. Para o icosaedro: 20→80→320→128020 \to 80 \to 320 \to 1280
20→80→320→1280 faces.

Tabela hash para unificação de vértices
Esse foi o detalhe mais sutil da implementação. Triângulos adjacentes compartilham arestas. Quando subdivido dois triângulos vizinhos, o ponto médio da aresta compartilhada é calculado duas vezes — uma por cada face. Se não unificar esses vértices, a malha fica com costuras, a fórmula de Euler não fecha, e o arquivo OBJ fica com geometria duplicada.
A solução é a tabela hash sugerida no enunciado: antes de inserir um vértice, arredondo suas coordenadas para 8 casas decimais e uso a tupla (round(x,8),round(y,8),round(z,8))(round(x, 8), round(y, 8), round(z, 8))
(round(x,8),round(y,8),round(z,8)) como chave. Se a chave já existe no dicionário, retorno o índice existente. Isso garante zero duplicatas, mesmo com erros de ponto flutuante.

pythondef _chave(self, v):
    return (round(v[0], self.precisao),
            round(v[1], self.precisao),
            round(v[2], self.precisao))
Resultados visuais
Evolução do icosaedro (nível 0 → 3):
Show Image
Comparação dos 3 sólidos platônicos (3 níveis de subdivisão):
Show Image
Métricas de qualidade (3 níveis de refinamento):
SólidoVérticesFacesRazão de áreasEuler (V−E+F)Erro de áreaTetraedro1302566.522 ✓0.21%Octaedro2585122.092 ✓0.32%Icosaedro64212801.292 ✓0.48%
A razão de áreas (maior triângulo / menor triângulo) é a métrica mais reveladora: o icosaedro produz triângulos quase iguais (razão 1.29), enquanto o tetraedro tem triângulos muito desiguais (6.52). Todos os vértices estão na esfera unitária com erro de norma da ordem de 10−1610^{-16}
10−16 (precisão de ponto flutuante IEEE 754).

Dificuldades na Tarefa 2
A primeira dificuldade foi a orientação consistente dos triângulos. Ao subdividir, é preciso manter a orientação (sentido anti-horário visto de fora) em todos os 4 subtriângulos. Se errar a ordem dos vértices em algum, as normais ficam invertidas e a renderização mostra "buracos" na malha. Levei um tempo debugando isso visualmente.
A segunda foi entender por que a precisão do arredondamento importa tanto na tabela hash. Com 6 casas decimais, alguns vértices que deveriam ser unificados não eram (ficavam com chaves diferentes por erro de arredondamento). Com 10 casas, o risco era o oposto — dois vértices genuinamente diferentes colapsarem na mesma chave. O valor de 8 casas funcionou bem para todos os casos testados, mas entendo que em malhas com muito mais níveis de refinamento isso precisaria ser ajustado com mais cuidado.
A terceira dificuldade — mais geométrica — foi perceber que a projeção na esfera deforma os triângulos de maneira não-uniforme, e que essa deformação depende do sólido inicial. O tetraedro tem faces que cobrem porções muito desiguais da esfera (cada face cobre quase um hemisfério!), então a subdivisão herda essa desigualdade. O icosaedro, com faces menores e mais uniformes, sofre menos. Isso explica a diferença nas razões de área e é a razão pela qual domos geodésicos reais usam o icosaedro.

Conexão entre as duas tarefas
As duas tarefas exploram representações complementares em modelagem geométrica:

Tarefa 1: representação implícita — o objeto é definido por uma função f(x,y)f(x,y)
f(x,y), e a enumeração espacial classifica o espaço ao redor. O refinamento adaptativo (Quadtree) concentra resolução na fronteira.

Tarefa 2: representação por fronteira (B-rep) — o objeto é definido pela sua superfície, uma malha de triângulos. A subdivisão refina a aproximação, e a projeção garante que os vértices permanecem na superfície desejada.

O tema unificador é o refinamento adaptativo: não gastar resolução onde não precisa, e investir resolução onde a geometria é mais complexa. Na Quadtree, isso significa subdividir só as células de fronteira. Na esfera geodésica, cada nível de subdivisão aproxima melhor a curvatura — mas a distribuição de qualidade depende do ponto de partida.

Como rodar
bash# Dependências
pip install matplotlib numpy

# Tarefa 1 — gera imagens dos discos, parábolas e refinamento
python3 tarefa1_celular.py

# Tarefa 2 — gera arquivos OBJ e imagens das esferas
python3 tarefa2_geodesica.py
As imagens e arquivos .obj são salvos na mesma pasta do script. Os .obj podem ser abertos em MeshLab, Blender ou qualquer visualizador 3D.

Tecnologias

Python 3.11+
NumPy — operações vetoriais e normalização de vértices
Matplotlib — visualização 2D (quadtree) e 3D (malhas triangulares)
Formato Wavefront OBJ — exportação das malhas


Referências

Bolzano, B. (1817). Rein analytischer Beweis des Lehrsatzes, dass zwischen je zwey Werthen, die ein entgegengesetztes Resultat gewähren, wenigstens eine reelle Wurzel der Gleichung liege. — Prova analítica do TVI, base teórica da classificação de células.
Finkel, R. A. e Bentley, J. L. (1974). Quad Trees: A Data Structure for Retrieval on Composite Keys. Acta Informatica, 4(1), 1–9. — Estrutura de dados Quadtree usada na enumeração adaptativa.
Suffern, K. G. (1990). Quadtree algorithms for contouring functions of two variables. The Computer Journal, 33(5), 402–407. — Refinamento adaptativo via Quadtree para contorno de funções implícitas.
Fuller, R. B. (1954). Building construction (U.S. Patent 2,682,235). — Patente do domo geodésico, aplicação prática da subdivisão icosaédrica.
Figueiredo, L. H. (2026). Notas de aula — Modelagem Geométrica, IMPA. — Referência principal do curso, incluindo classificação de caixas, enumeração espacial e representação por fronteira.


Licença
Trabalho acadêmico para o curso de Modelagem Geométrica, IMPA — Verão 2026.
