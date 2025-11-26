Test checklist - Verificações manuais antes do deploy

Objetivo
- Validar interacções dinâmicas dos `selectbox` e campos dependentes (paginas: Escuteiros, Blocos de Rifas, Recebimento, Devoluções).

Preparação
- A branch com as alterações deve estar atualizada no remoto (`git push`).
- Iniciar a app localmente: `streamlit run app.py`.
- Ter alguns dados de teste: pelo menos 3 escuteiros ativos, 5 blocos criados numa campanha, alguns blocos atribuídos e outros disponíveis.

Checklist (passos manuais)

1) Página: `👥 Escuteiros`
- A) Abrir tab `Editar/Eliminar`.
- B) Verificar que o seletor "Selecione um escuteiro" mostra nomes corretamente e não causa erro ao selecionar diferentes entradas.
- C) Seleccionar um escuteiro diferente e confirmar que os campos do formulário (`Nome`, `Email`, `Telefone`) actualizam para os valores do escuteiro seleccionado.
- D) Editar um campo e submeter; confirmar que a alteração é aplicada e a página recarrega.

2) Página: `🎟️ Blocos de Rifas` -> Tab `Atribuição de Secção`
- A) Seleccionar `Bloco Inicial` e `Bloco Final` e confirmar que o intervalo exibido e o número de blocos a atribuir actualizam corretamente.
- B) Testar limites: seleccionar o mesmo bloco para início e fim; seleccionar o primeiro bloco da lista para início e o último para fim.
- C) Submeter atribuição e verificar que a base de dados (e UI após reload) reflecte a alteração.

3) Página: `🎟️ Blocos de Rifas` -> Tab `Atribuir Bloco a Escuteiro`
- A) Modo `Irmãos`: seleccionar um bloco e múltiplos irmãos via multiselect. Confirmar que a pré-visualização mostra os nomes correctos (não ids) e intervalos correctos.
- B) Confirmar que o bloco é dividido e atribuído aos escuteiros correspondentes.
- C) Modo `Individual`: seleccionar um bloco, mudar a opção de escuteiro (usar o selector id-based) e submeter; verificar que a atribuição é guardada.

4) Página: `📦 Recebimento` -> Tab `Registar Novo Recebimento`
- A) Seleccionar vários blocos diferentes; confirmar que `Valor do Bloco`, `Saldo Pendente` e `Total de Rifas` actualizam conforme o bloco seleccionado.
- B) Mudar o valor do `Valor Recebido` e `Canhotos Entregues`, submeter e confirmar que o registo é criado e a página recarrega.
- C) Editar um recebimento existente: abrir editor, mudar o bloco seleccionado e verificar que os campos (ex.: default de `rifas_entregues`) actualizam para o novo bloco.

5) Página: `🔄 Devoluções`
- A) Seleccionar blocos diferentes e confirmar que a mensagem "Este bloco tem X rifas no total" actualiza.
- B) Confirmar que o `Quantidade de Rifas Devolvidas` assume por default o total do bloco e que o `max_value` é o total do bloco.
- C) Submeter uma devolução (testar) e confirmar que o registo aparece na lista.

6) Checks gerais
- A) Não deve haver mensagens de debug visíveis nas páginas testeadas.
- B) Procurar erros no terminal do Streamlit (excepções ou traces) durante as interacções.
- C) Testar navegação entre páginas e garantir que a selecção de campanha mantém o filtro correcto.

Notas de troubleshooting
- Se um `selectbox` mostrar um rótulo diferente do valor actual (desincronização), recarregar a página (`Ctrl+R`) para limpar `st.session_state` e repetir a selecção.
- Se existirem keys antigas em `st.session_state` (ver no código), considerar limpá-las ou reiniciar a sessão do Streamlit.

Fim do checklist
