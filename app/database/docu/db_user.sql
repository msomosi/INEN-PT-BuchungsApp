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
-- Name: tbl_rolle; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.tbl_rolle (
    role_id integer NOT NULL,
    role_name character(1)
);


ALTER TABLE public.tbl_rolle OWNER TO ubuntu;

--
-- Name: tbl_rolle_role_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_rolle_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_rolle_role_id_seq OWNER TO ubuntu;

--
-- Name: tbl_rolle_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_rolle_role_id_seq OWNED BY public.tbl_rolle.role_id;


--
-- Name: tbl_user; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.tbl_user (
    user_id bigint NOT NULL,
    role_id integer NOT NULL,
    verification boolean,
    verification_date date,
    username character(20),
    password character(500)
);


ALTER TABLE public.tbl_user OWNER TO ubuntu;

--
-- Name: tbl_user_details; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.tbl_user_details (
    user_id integer NOT NULL,
    "CompanyName" character(50),
    "Firstname" character(20),
    "Lastname" character(20),
    "Matrikelnummer" integer NOT NULL,
    "University" character(50),
    "Inskription_end" integer NOT NULL,
    "Adresse" character(100),
    "Plz" integer NOT NULL,
    "Location" character(50),
    notice character(800),
    email character(100),
    phone character(25)
);


ALTER TABLE public.tbl_user_details OWNER TO ubuntu;

--
-- Name: tbl_user_details_Inskription_end_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public."tbl_user_details_Inskription_end_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."tbl_user_details_Inskription_end_seq" OWNER TO ubuntu;

--
-- Name: tbl_user_details_Inskription_end_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public."tbl_user_details_Inskription_end_seq" OWNED BY public.tbl_user_details."Inskription_end";


--
-- Name: tbl_user_details_Matrikelnummer_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public."tbl_user_details_Matrikelnummer_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."tbl_user_details_Matrikelnummer_seq" OWNER TO ubuntu;

--
-- Name: tbl_user_details_Matrikelnummer_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public."tbl_user_details_Matrikelnummer_seq" OWNED BY public.tbl_user_details."Matrikelnummer";


--
-- Name: tbl_user_details_Plz_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public."tbl_user_details_Plz_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."tbl_user_details_Plz_seq" OWNER TO ubuntu;

--
-- Name: tbl_user_details_Plz_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public."tbl_user_details_Plz_seq" OWNED BY public.tbl_user_details."Plz";


--
-- Name: tbl_user_details_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_user_details_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_user_details_user_id_seq OWNER TO ubuntu;

--
-- Name: tbl_user_details_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_user_details_user_id_seq OWNED BY public.tbl_user_details.user_id;


--
-- Name: tbl_user_role_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_user_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_user_role_id_seq OWNER TO ubuntu;

--
-- Name: tbl_user_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_user_role_id_seq OWNED BY public.tbl_user.role_id;


--
-- Name: tbl_user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE public.tbl_user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_user_user_id_seq OWNER TO ubuntu;

--
-- Name: tbl_user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE public.tbl_user_user_id_seq OWNED BY public.tbl_user.user_id;


--
-- Name: tbl_rolle role_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_rolle ALTER COLUMN role_id SET DEFAULT nextval('public.tbl_rolle_role_id_seq'::regclass);


--
-- Name: tbl_user user_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user ALTER COLUMN user_id SET DEFAULT nextval('public.tbl_user_user_id_seq'::regclass);


--
-- Name: tbl_user role_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user ALTER COLUMN role_id SET DEFAULT nextval('public.tbl_user_role_id_seq'::regclass);


--
-- Name: tbl_user_details user_id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user_details ALTER COLUMN user_id SET DEFAULT nextval('public.tbl_user_details_user_id_seq'::regclass);


--
-- Name: tbl_user_details Matrikelnummer; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user_details ALTER COLUMN "Matrikelnummer" SET DEFAULT nextval('public."tbl_user_details_Matrikelnummer_seq"'::regclass);


--
-- Name: tbl_user_details Inskription_end; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user_details ALTER COLUMN "Inskription_end" SET DEFAULT nextval('public."tbl_user_details_Inskription_end_seq"'::regclass);


--
-- Name: tbl_user_details Plz; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user_details ALTER COLUMN "Plz" SET DEFAULT nextval('public."tbl_user_details_Plz_seq"'::regclass);


--
-- Name: tbl_rolle tbl_rolle_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_rolle
    ADD CONSTRAINT tbl_rolle_pkey PRIMARY KEY (role_id);


--
-- Name: tbl_user_details tbl_user_details_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user_details
    ADD CONSTRAINT tbl_user_details_pkey PRIMARY KEY (user_id);


--
-- Name: tbl_user fk_rolle_roleid; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user
    ADD CONSTRAINT fk_rolle_roleid FOREIGN KEY (role_id) REFERENCES public.tbl_rolle(role_id);


--
-- Name: tbl_user fk_user_userid; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.tbl_user
    ADD CONSTRAINT fk_user_userid FOREIGN KEY (user_id) REFERENCES public.tbl_user_details(user_id);


--
-- PostgreSQL database dump complete
--

