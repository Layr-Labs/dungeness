---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 41
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 41

The text below is a page-delimited extraction of the unchanged source PDF.

Davies, Sebastian Nowozin, Pushmeet Kohli, and Matej Balog. AlphaEvolve: A cod-
ing agent for scientific and algorithmic discovery.arXiv preprint arXiv:2506.13131, 2025.
arXiv:2506.13131
[GP13] Nicola Guglielmi and Vladimir Protasov. Exact computation of joint spectral character-
istics of linear operators.Foundations of Computational Mathematics, 13(1):37–97, 2013.
https://doi.org/10.1007/s10208-012-9121-0.
[YLT+26] Haotian Ye, Haowei Lin, Jingyi Tang, Yizhen Luo, Rahul Thapa, Caiyin Yang, Chang
Su, Rui Yang, Ruihua Liu, Rundao Li, Zeyu Li, Pengwei Sun, Chong Gao, Dachao Ding,
Guangrong He, Miaolei Zhang, Lina Sun, Wenyang Wang, Yuchen Zhong, Zhuohao Shen,
Puheng Li, Pan Lu, Bianxiao Cui, Di He, Jianzhu Ma, Junfeng Li, Hexi Baoyin, Yejin
Choi, Stefano Ermon, Xiaowen Chu, Tongyang Li, Yuzhi Xu, and James Zou.
Structured scaling of AI discovery across diverse scientific domains.
arXiv preprint arXiv:2604.19341, 2026.
https://arxiv.org/abs/2604.19341.
A Proof Details
A.1 Bounds on the total number of steps
Suppose that aftermiterations of the Extended Euclidean Algorithm, we obtainr m = 1 andr m+1 = 0,
with intermediate quotientsq1, q2, . . . , qm, whereq i =⌊r i−1/ri⌋fori= 1,2, . . . , m. Then the total number
of steps required in our four-phase algorithm can be expressed as
N= 4
mX
i=1
(⌊log2 qi⌋+ 1).(9)
In this appendix, we prove that 4n≤N≤4⌈cn⌉, wherec= 3/log 2(2 +
√
3).
The lower bound.The lower bound ofNcan be derived directly. Sincer i−1 =q iri +ri+1 <(q i +1)ri,
it follows that
N≥4
mX
i=1
log2(qi + 1)>4
mX
i=1
log2
ri−1
ri
= 4 log2 p≥4(n−1).
BecauseNmust be a multiple of 4, we conclude thatN≥4n.
Asymptotic sharpness of the upper bound.Before we moving on to the proof of the upper bound,
we first express why the constantc= 3/log 2(2 +
√
3) in the upper boundN≤4⌈cn⌉is asymptotically
optimal. We consider a different roadmap from deriving the lower bound: instead of computing the upper
bound ofN, we fix the total number of stepsNand then compute the minimum possible value ofp.
41
