--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tbl_zimmer; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.tbl_zimmer (
    zimmer_id bigint NOT NULL,
    user_id bigint NOT NULL,
    date_from date,
    date_to date
);


ALTER TABLE public.tbl_zimmer OWNER TO ubuntu;

--
-- Name: tbl_zimmer_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_zimmer_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_zimmer_user_id_seq OWNER TO ubuntu;

--
-- Name: tbl_zimmer_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_zimmer_user_id_seq OWNED BY public.tbl_zimmer.user_id;


--
-- Name: tbl_zimmer_zimmer_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_zimmer_zimmer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_zimmer_zimmer_id_seq OWNER TO ubuntu;

--
-- Name: tbl_zimmer_zimmer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_zimmer_zimmer_id_seq OWNED BY public.tbl_zimmer.zimmer_id;


--
-- Name: tbl_zimmer zimmer_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_zimmer ALTER COLUMN zimmer_id SET DEFAULT nextval('public.tbl_zimmer_zimmer_id_seq'::regclass);


--
-- Name: tbl_zimmer user_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_zimmer ALTER COLUMN user_id SET DEFAULT nextval('public.tbl_zimmer_user_id_seq'::regclass);


--
-- Name: tbl_zimmer tbl_zimmer_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_zimmer
    ADD CONSTRAINT tbl_zimmer_pkey PRIMARY KEY (zimmer_id);


--
-- Name: tbl_zimmer tbl_zimmer_user_id_key; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_zimmer
    ADD CONSTRAINT tbl_zimmer_user_id_key UNIQUE (user_id);


--
-- PostgreSQL database dump complete
--

