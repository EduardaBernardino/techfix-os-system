-- Script de Criação do Banco de Dados para TechFix Informática
-- Extensão para geração de UUID caso necessária no futuro (opcional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabela de Clientes
CREATE TABLE IF NOT EXISTS public.clientes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    celular_whatsapp TEXT NOT NULL,
    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Validação do e-mail com regex simples
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    -- Validação do celular/WhatsApp: apenas números, entre 10 e 13 dígitos
    CONSTRAINT check_celular_format CHECK (celular_whatsapp ~ '^[0-9]{10,13}$')
);

-- 2. Tabela de Ordens de Serviço
CREATE TABLE IF NOT EXISTS public.ordens_servico (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    modelo_computador TEXT NOT NULL,
    problema_relatado TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Aberto',
    data_abertura TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    data_atualizacao TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Chave estrangeira ligando à tabela de clientes com exclusão em cascata
    CONSTRAINT fk_ordens_servico_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(id)
        ON DELETE CASCADE,

    -- Restrição CHECK para validar os status permitidos
    CONSTRAINT check_status_validos CHECK (
        status IN ('Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue')
    )
);

-- Função e Trigger para atualizar automaticamente a data_atualizacao ao modificar uma OS
CREATE OR REPLACE FUNCTION update_data_atualizacao_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.data_atualizacao = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_ordens_servico_modtime
BEFORE UPDATE ON public.ordens_servico
FOR EACH ROW
EXECUTE FUNCTION update_data_atualizacao_column();