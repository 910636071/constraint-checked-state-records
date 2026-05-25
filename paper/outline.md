r_t: normalized symbolic record
s_t: intermediate state
m: method identifier
C: constraint set
z_t: checked output record
q: aggregate score

s_t = F(s_{t-1}, r_t)
p_t = G(s_t, m)
z_t = H(p_t, C)
q = A({z_t})
