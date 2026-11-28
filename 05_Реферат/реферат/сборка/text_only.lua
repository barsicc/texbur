-- Убираем графические блоки, подписи и таблицы для контрольного замера.
function Figure()
  return {}
end

function Table()
  return {}
end

function Para(block)
  if pandoc.utils.stringify(block):match("^Таблица [1-5] —") then
    return {}
  end
end
