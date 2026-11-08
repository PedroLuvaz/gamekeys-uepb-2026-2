-- GK-128: uma linha por chave vinculada a pedidos distintos, sem ler códigos.
select c.id as chave_id,
       c.jogo_id,
       array_agg(distinct i.pedido_id order by i.pedido_id) as pedido_ids
  from catalogo.chaves as c
  join vendas.itens_pedido as i on i.chave_id = c.id
 group by c.id, c.jogo_id
having count(distinct i.pedido_id) > 1
 order by c.id;
