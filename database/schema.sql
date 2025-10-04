-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.arquivos_chat (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  mensagem_id bigint NOT NULL,
  nome_arquivo character varying NOT NULL,
  url_arquivo character varying NOT NULL,
  tipo_arquivo character varying,
  tamanho_bytes bigint,
  data_upload timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT arquivos_chat_pkey PRIMARY KEY (id),
  CONSTRAINT arquivos_chat_mensagem_id_fkey FOREIGN KEY (mensagem_id) REFERENCES public.mensagens(id)
);
CREATE TABLE public.chats (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  projeto_id bigint NOT NULL,
  tipo_ia_id bigint NOT NULL,
  titulo character varying NOT NULL,
  data_criacao timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chats_pkey PRIMARY KEY (id),
  CONSTRAINT chats_projeto_id_fkey FOREIGN KEY (projeto_id) REFERENCES public.projetos(id),
  CONSTRAINT chats_tipo_ia_id_fkey FOREIGN KEY (tipo_ia_id) REFERENCES public.tipos_ia(id)
);
CREATE TABLE public.mensagens (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  chat_id bigint NOT NULL,
  usuario_id bigint,
  conteudo text NOT NULL,
  e_nota_orientador boolean DEFAULT false,
  data_envio timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT mensagens_pkey PRIMARY KEY (id),
  CONSTRAINT mensagens_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id),
  CONSTRAINT mensagens_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id)
);
CREATE TABLE public.orientadores_projetos (
  orientador_id bigint NOT NULL,
  projeto_id bigint NOT NULL,
  CONSTRAINT orientadores_projetos_pkey PRIMARY KEY (orientador_id, projeto_id),
  CONSTRAINT orientadores_projetos_orientador_id_fkey FOREIGN KEY (orientador_id) REFERENCES public.usuarios(id),
  CONSTRAINT orientadores_projetos_projeto_id_fkey FOREIGN KEY (projeto_id) REFERENCES public.projetos(id)
);
CREATE TABLE public.participantes_projetos (
  participante_id bigint NOT NULL,
  projeto_id bigint NOT NULL,
  CONSTRAINT participantes_projetos_pkey PRIMARY KEY (participante_id, projeto_id),
  CONSTRAINT participantes_projetos_participante_id_fkey FOREIGN KEY (participante_id) REFERENCES public.usuarios(id),
  CONSTRAINT participantes_projetos_projeto_id_fkey FOREIGN KEY (projeto_id) REFERENCES public.projetos(id)
);
CREATE TABLE public.projetos (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome character varying NOT NULL,
  descricao text,
  area_projeto character varying NOT NULL,
  ano_edicao integer NOT NULL,
  data_criacao timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT projetos_pkey PRIMARY KEY (id)
);
CREATE TABLE public.tipos_ia (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome character varying NOT NULL UNIQUE,
  CONSTRAINT tipos_ia_pkey PRIMARY KEY (id)
);
CREATE TABLE public.tipos_usuario (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome character varying NOT NULL UNIQUE,
  CONSTRAINT tipos_usuario_pkey PRIMARY KEY (id)
);
CREATE TABLE public.usuarios (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome_completo character varying NOT NULL,
  email character varying NOT NULL UNIQUE,
  senha_hash character varying,
  tipo_usuario_id bigint NOT NULL,
  bp character varying UNIQUE,
  data_criacao timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  data_atualizacao timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT usuarios_pkey PRIMARY KEY (id),
  CONSTRAINT usuarios_tipo_usuario_id_fkey FOREIGN KEY (tipo_usuario_id) REFERENCES public.tipos_usuario(id)
);