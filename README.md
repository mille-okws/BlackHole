# Buraco Negro de Schwarzschild — Ray Tracing Relativístico

> **🚧 WIP — Work in Progress**

Simulação numérica da propagação da luz nas proximidades de um buraco negro de Schwarzschild utilizando geodésicas da Relatividade Geral.

O objetivo do projeto é construir um **ray tracer relativístico** capaz de reproduzir numericamente fenômenos como **lente gravitacional, esfera de fótons e sombra aparente de um buraco negro**.

---

## Sobre o projeto

Este projeto implementa um modelo numérico de um **buraco negro de Schwarzschild**, considerando:

* buraco negro não rotativo;
* carga elétrica nula;
* espaço-tempo isolado;
* Relatividade Geral;
* unidades geométricas \(G=c=M=1\).

A base física do projeto é a **métrica de Schwarzschild** e a equação das **geodésicas**.

Para um raio de luz, a trajetória é obtida pela integração numérica de

$$
\frac{d^2x^\mu}{d\lambda^2}
+
\Gamma^\mu_{\alpha\beta}
\frac{dx^\alpha}{d\lambda}
\frac{dx^\beta}{d\lambda}
=0
$$

sujeita à condição de geodésica nula

$$
g_{\mu\nu}
\frac{dx^\mu}{d\lambda}
\frac{dx^\nu}{d\lambda}=0.
$$

A ideia central é lançar raios a partir de uma **câmera virtual**, integrar suas trajetórias para trás através do espaço-tempo e determinar o que cada pixel da imagem observaria.

---

## Estado atual

### Modelo físico

* [x] Métrica de Schwarzschild
* [x] Símbolos de Christoffel
* [x] Equações das geodésicas
* [x] Integração numérica
* [x] Horizonte de eventos
* [x] Esfera de fótons
* [x] Órbitas circulares
* [x] ISCO
* [x] Limite de espaço plano
* [x] Limite newtoniano
* [x] Validação da precessão do periélio

### Visualização

* [x] Renderer 2D
* [x] Horizonte de eventos
* [x] Esfera de fótons
* [x] ISCO
* [x] Trajetórias das geodésicas
* [ ] Modelo de câmera
* [ ] Geração de raios
* [ ] Ray tracing relativístico
* [ ] Sombra do buraco negro
* [ ] Lente gravitacional
* [ ] Campo de estrelas
* [ ] Disco de acreção
* [ ] Redshift gravitacional
* [ ] Efeito Doppler relativístico

---

# Modelo físico

A métrica de Schwarzschild é dada por

$$
ds^2 =
-\left(1-\frac{2M}{r}\right)c^2dt^2
+
\left(1-\frac{2M}{r}\right)^{-1}dr^2
+
r^2d\theta^2
+
r^2\sin^2\theta\,d\phi^2.
$$

Neste projeto são utilizadas unidades geométricas:

$$
G=c=M=1.
$$

Assim,

$$
ds^2 =
-\left(1-\frac{2}{r}\right)dt^2
+
\left(1-\frac{2}{r}\right)^{-1}dr^2
+
r^2d\theta^2
+
r^2\sin^2\theta\,d\phi^2.
$$

As principais escalas características do sistema são:

| Estrutura            |   Raio |
| -------------------- | -----: |
| Horizonte de eventos | \(2M\) |
| Esfera de fótons     | \(3M\) |
| ISCO                 | \(6M\) |

---

## Geodésicas

O estado utilizado na integração é

$$
\mathbf{y}
=
(t,r,\theta,\phi,
\dot{t},\dot{r},\dot{\theta},\dot{\phi}).
$$

A dinâmica é escrita como

$$
\dot{x}^{\mu}=u^\mu
$$

e

$$
\dot{u}^{\mu}
=
-\Gamma^\mu_{\alpha\beta}
u^\alpha u^\beta.
$$

Para fótons, a trajetória deve satisfazer

$$
g_{\mu\nu}u^\mu u^\nu=0.
$$

Dessa forma, a propagação da luz é determinada pela geometria do espaço-tempo, e não por uma aproximação newtoniana.

---

# Validação física

Antes de utilizar o modelo para produzir imagens, suas propriedades físicas são verificadas numericamente.

Resultados atuais:

```text
[Teste 1] Espaço plano (M->0): dr aprox. constante = True
[Teste 2] Limite newtoniano: erro relativo = 0.0004, ok = True
[Teste 3] Captura no horizonte: motivo=capture, r_final=2.0020, ok=True
[Teste 4] Esfera de fótons: desvio máx. de 3M = 0.0000, ok=True
[Teste 5a] Órbita circular estável em r=10.0M: desvio máx.=0.0000, ok=True
[Teste 5b] ISCO em r=6M: desvio máx.=0.0000, ok=True
[Teste 6] Precessão: numérico=0.356577, esperado=0.329867, erro rel.=0.0810, ok=True

=== Resumo ===
flat_space: OK
newtonian_limit: OK
event_horizon: OK
photon_sphere: OK
circular_orbit: OK
isco: OK
precession: OK
```

A validação é importante porque o objetivo do projeto é gerar a imagem a partir da dinâmica relativística, e não simplesmente desenhar um buraco negro visualmente convincente.

---

# Ray Tracing

A próxima etapa do projeto é implementar **ray tracing relativístico**.

A abordagem escolhida será o **backward ray tracing**.

Em vez de emitir milhões de fótons a partir do buraco negro, cada pixel da câmera gera um raio que é propagado **para trás** através do espaço-tempo.

```text
                 CÂMERA

        ┌───────────────────────┐
        │ • • • • • • • • • • │
        │ • • • • • • • • • • │
        │ • • • • • • • • • • │
        └───────────────────────┘
             \   |   |   /
              \  |   |  /
               \ |   | /
                \|   |/
                 \   /
                  \ /
                  (●)
             BURACO NEGRO
```

Para cada pixel:

1. determinar a posição da câmera;
2. determinar a direção do raio;
3. construir as condições iniciais do fóton;
4. garantir a condição nula \(ds^2=0\);
5. integrar a geodésica;
6. verificar se o raio é capturado ou escapa;
7. determinar a origem aparente do raio;
8. atribuir uma cor ao pixel.

O resultado será uma imagem construída diretamente a partir das trajetórias dos fótons.

---

# Sombra do buraco negro

Um dos primeiros resultados esperados é a obtenção da **sombra aparente** do buraco negro.

O raio crítico da órbita de fótons para um observador distante está relacionado ao parâmetro de impacto crítico:

$$
b_{\mathrm{crit}} = 3\sqrt{3}\,M.
$$

Isso é importante porque a sombra observada não corresponde simplesmente ao círculo físico do horizonte

$$
r=2M.
$$

A curvatura do espaço-tempo faz com que fótons que passam fora do horizonte também possam ser capturados.

A fronteira da sombra emerge naturalmente da classificação entre:

```text
                 FÓTONS QUE ESCAPAM
                        ↑
                 \      |      /
                  \     |     /
                   \    |    /
                    \   |   /
                     \  |  /
                      \ | /
                       \|/
                      ( ● )
                       /|\
                      / | \
                     /  |  \
                    /   |   \
                 FÓTONS CAPTURADOS
```

---

# Lente gravitacional

Os raios que passam próximos à esfera de fótons sofrerão grandes desvios angulares.

O ray tracer deverá permitir observar:

* desvio gravitacional da luz;
* lente gravitacional fraca;
* lente gravitacional forte;
* trajetórias altamente defletidas;
* múltiplas imagens;
* anéis de Einstein em configurações apropriadas.

---

# Campo de estrelas

Uma etapa posterior será implementar um campo de estrelas como background.

Sem o buraco negro:

```text
★       ★           ★

    ★          ★

          ★

 ★              ★
```

Com o buraco negro, os raios provenientes dessas estrelas serão desviados pela geometria do espaço-tempo.

Assim, a distorção do campo visual será consequência direta do ray tracing.

---

# Disco de acreção

Depois da implementação da sombra e da lente gravitacional, será adicionado um **disco de acreção**.

Nesse estágio, cada raio poderá:

1. ser lançado pela câmera;
2. atravessar o espaço-tempo;
3. interceptar o disco;
4. determinar a posição do ponto emissor;
5. calcular a contribuição de luz observada.

Posteriormente poderão ser incluídos efeitos relativísticos como:

* redshift gravitacional;
* blueshift gravitacional;
* efeito Doppler;
* velocidade orbital do material;
* variação da intensidade observada.

---

# Arquitetura

O projeto separa o modelo físico da visualização.

```text
black_hole/
│
├── physics/
│   ├── metric.py
│   ├── christoffel.py
│   ├── geodesic.py
│   ├── constants.py
│   └── initial_conditions.py
│
├── simulation/
│   ├── integrator.py
│   ├── events.py
│   └── trajectories.py
│
├── validation/
│   ├── newtonian_limit.py
│   ├── photon_sphere.py
│   ├── schwarzschild_radius.py
│   ├── circular_orbits.py
│   └── precession.py
│
├── renderer/
│   ├── renderer_2d.py
│   ├── geometry.py
│   ├── styles.py
│   └── camera.py
│
├── raytracing/
│   ├── camera.py
│   ├── rays.py
│   ├── integrator.py
│   ├── events.py
│   ├── background.py
│   └── renderer.py
│
└── main.py
```

A arquitetura segue o fluxo:

```text
       MODELO FÍSICO
             │
             ▼
     INTEGRAÇÃO NUMÉRICA
             │
             ▼
         GEODÉSICA
             │
             ▼
        RAY TRACING
             │
             ▼
           PIXEL
             │
             ▼
          IMAGEM
```

O renderer não deve calcular a física do buraco negro. Ele recebe os resultados da simulação e os transforma em informação visual.

---

# Tecnologias

* **Python**
* **NumPy**
* **SciPy**
* **Matplotlib**

O objetivo é implementar o modelo diretamente a partir das equações físicas, evitando depender de um motor pronto de simulação ou renderização de buracos negros.

---

# Roadmap

```text
[x] Métrica de Schwarzschild
[x] Símbolos de Christoffel
[x] Equações das geodésicas
[x] Integração numérica
[x] Validação física
[x] Renderer 2D
[x] Visualização das geodésicas

[ ] Modelo de câmera
[ ] Geração dos raios
[ ] Ray tracing de geodésicas nulas
[ ] Classificação captura/escape
[ ] Sombra do buraco negro
[ ] Lente gravitacional
[ ] Campo de estrelas
[ ] Disco de acreção
[ ] Redshift gravitacional
[ ] Efeito Doppler relativístico
[ ] Renderização em alta resolução
[ ] Otimização de performance
```

---

# Status

**🚧 WIP — Work in Progress**

O modelo relativístico e a bateria principal de validações físicas já estão implementados.

O projeto está atualmente migrando da simulação de **geodésicas individuais** para o **ray tracing pixel a pixel**.

O objetivo final é construir um renderer no qual a imagem observada seja uma consequência direta da propagação dos fótons pelo espaço-tempo curvo de Schwarzschild.
