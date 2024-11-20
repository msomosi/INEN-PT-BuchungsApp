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
-- Name: tbl_booking_state; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.tbl_booking_state (
    state_id integer NOT NULL,
    state_name character(25)
);


ALTER TABLE public.tbl_booking_state OWNER TO ubuntu;

--
-- Name: tbl_booking_state_state_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_booking_state_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_booking_state_state_id_seq OWNER TO ubuntu;

--
-- Name: tbl_booking_state_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_booking_state_state_id_seq OWNED BY public.tbl_booking_state.state_id;


--
-- Name: tbl_buchung; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.tbl_buchung (
    buchung_id integer NOT NULL,
    user_id bigint NOT NULL,
    zimmer_id bigint NOT NULL,
    date_from date NOT NULL,
    date_to date NOT NULL,
    state_id integer NOT NULL
);


ALTER TABLE public.tbl_buchung OWNER TO ubuntu;

--
-- Name: tbl_buchung_buchung_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_buchung_buchung_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_buchung_buchung_id_seq OWNER TO ubuntu;

--
-- Name: tbl_buchung_buchung_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_buchung_buchung_id_seq OWNED BY public.tbl_buchung.buchung_id;


--
-- Name: tbl_buchung_state_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_buchung_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_buchung_state_id_seq OWNER TO ubuntu;

--
-- Name: tbl_buchung_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_buchung_state_id_seq OWNED BY public.tbl_buchung.state_id;


--
-- Name: tbl_buchung_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_buchung_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_buchung_user_id_seq OWNER TO ubuntu;

--
-- Name: tbl_buchung_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_buchung_user_id_seq OWNED BY public.tbl_buchung.user_id;


--
-- Name: tbl_buchung_zimmer_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_buchung_zimmer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_buchung_zimmer_id_seq OWNER TO ubuntu;

--
-- Name: tbl_buchung_zimmer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_buchung_zimmer_id_seq OWNED BY public.tbl_buchung.zimmer_id;


--
-- Name: tbl_booking_state state_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_booking_state ALTER COLUMN state_id SET DEFAULT nextval('public.tbl_booking_state_state_id_seq'::regclass);


--
-- Name: tbl_buchung buchung_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_buchung ALTER COLUMN buchung_id SET DEFAULT nextval('public.tbl_buchung_buchung_id_seq'::regclass);


--
-- Name: tbl_buchung user_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_buchung ALTER COLUMN user_id SET DEFAULT nextval('public.tbl_buchung_user_id_seq'::regclass);


--
-- Name: tbl_buchung zimmer_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_buchung ALTER COLUMN zimmer_id SET DEFAULT nextval('public.tbl_buchung_zimmer_id_seq'::regclass);


--
-- Name: tbl_buchung state_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_buchung ALTER COLUMN state_id SET DEFAULT nextval('public.tbl_buchung_state_id_seq'::regclass);


--
-- Name: tbl_booking_state tbl_booking_state_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_booking_state
    ADD CONSTRAINT tbl_booking_state_pkey PRIMARY KEY (state_id);


--
-- Name: tbl_buchung tbl_buchung_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_buchung
    ADD CONSTRAINT tbl_buchung_pkey PRIMARY KEY (buchung_id);


--
-- Name: tbl_buchung fk_buchung_stateid; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_buchung
    ADD CONSTRAINT fk_buchung_stateid FOREIGN KEY (state_id) REFERENCES public.tbl_booking_state(state_id);


--
-- PostgreSQL database dump complete
--

