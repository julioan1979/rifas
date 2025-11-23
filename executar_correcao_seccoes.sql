-- Corrigir blocos 391-400 e 411-420 que são Lobitos (não Reserva)
UPDATE blocos_rifas 
SET seccao = 'Lobitos' 
WHERE (numero_inicial = 391 AND numero_final = 400)
   OR (numero_inicial = 411 AND numero_final = 420);

-- Verificar resultado
SELECT nome, seccao, numero_inicial, numero_final
FROM blocos_rifas
WHERE (numero_inicial = 391 AND numero_final = 400)
   OR (numero_inicial = 411 AND numero_final = 420);
