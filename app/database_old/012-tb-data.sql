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
-- Name: accommodation; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.accommodation (
    provider_id integer NOT NULL,
    contact_id integer NOT NULL,
    company_name character varying(50),
    parking boolean,
    parking_free boolean,
    free_notice character varying(500)
);


ALTER TABLE public.accommodation OWNER TO ubuntu;

--
-- Name: accommodation_provider_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public.accommodation ALTER COLUMN provider_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accommodation_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: booking; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.booking (
    booking_id integer NOT NULL,
    user_id integer NOT NULL,
    room_id integer NOT NULL,
    state_id integer NOT NULL
);


ALTER TABLE public.booking OWNER TO ubuntu;

--
-- Name: booking_booking_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public.booking ALTER COLUMN booking_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.booking_booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: booking_state; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.booking_state (
    state_id integer NOT NULL,
    state_name character varying(25)
);


ALTER TABLE public.booking_state OWNER TO ubuntu;

--
-- Name: booking_state_state_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public.booking_state ALTER COLUMN state_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.booking_state_state_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: contact; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.contact (
    contact_id integer NOT NULL,
    address character varying(50),
    postal_code numeric(4,0),
    location character varying(50),
    phone character varying(20)
);


ALTER TABLE public.contact OWNER TO ubuntu;

--
-- Name: contact_kontakt_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public.contact ALTER COLUMN contact_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.contact_kontakt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: role; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.role (
    role_id integer NOT NULL,
    role_name character varying(50)
);


ALTER TABLE public.role OWNER TO ubuntu;

--
-- Name: role_role_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public.role ALTER COLUMN role_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.role_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: room; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.room (
    room_id integer NOT NULL,
    provider_id integer NOT NULL,
    date date,
    state_id integer DEFAULT 1 NOT NULL
);


ALTER TABLE public.room OWNER TO ubuntu;

--
-- Name: room_room_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public.room ALTER COLUMN room_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.room_room_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: student; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.student (
    user_id integer NOT NULL,
    contact_id integer NOT NULL,
    student_number character varying(20),
    university_id integer NOT NULL,
    enrollment_end date
);


ALTER TABLE public.student OWNER TO ubuntu;

--
-- Name: university; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public.university (
    university_id integer NOT NULL,
    university_name character varying(50),
    contact_id integer NOT NULL
);


ALTER TABLE public.university OWNER TO ubuntu;

--
-- Name: university_university_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public.university ALTER COLUMN university_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.university_university_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user; Type: TABLE; Schema: public; Owner: ubuntu
--

CREATE TABLE public."user" (
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    provider_id integer,
    verification boolean,
    verification_date date,
    email character varying(50),
    oauth_token character varying(100),
    first_name character varying(50),
    last_name character varying(50)
);


ALTER TABLE public."user" OWNER TO ubuntu;

--
-- Name: user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

ALTER TABLE public."user" ALTER COLUMN user_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: accommodation; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.accommodation (provider_id, contact_id, company_name, parking, parking_free, free_notice) FROM stdin;
1	1	OEJAB Eisenstadt	t	t	
2	2	Hotel A	f	f	
999999999	999999999	student_only	\N	\N	
\.


--
-- Data for Name: booking; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.booking (booking_id, user_id, room_id, state_id) FROM stdin;
1	3	1	3
2	3	3	2
\.


--
-- Data for Name: booking_state; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.booking_state (state_id, state_name) FROM stdin;
1	available
2	pending
3	confirmed
4	completed
5	failed
\.


--
-- Data for Name: contact; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.contact (contact_id, address, postal_code, location, phone) FROM stdin;
1	Campus 2	7000	Eisenstadt	0126485682
2	Rechbauerstraße 12	8010	Graz	06642158713365
3	Student Address	1010	Vienna	06641234567
999999999	999999999	8010	999999999	999999999
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.role (role_id, role_name) FROM stdin;
1	admin
2	provider
3	student
\.


--
-- Data for Name: room; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.room (room_id, provider_id, date, state_id) FROM stdin;
2	1	2024-11-25	1
4	1	2024-11-26	1
5	1	2024-11-27	1
7	1	2024-11-29	1
8	1	2024-11-30	1
6	1	2024-11-27	2
9	1	2024-12-23	1
10	1	2025-01-06	1
11	1	2025-01-06	1
13	1	2025-01-07	1
14	1	2025-01-20	1
15	1	2025-01-21	1
16	1	2025-01-22	1
17	1	2025-01-23	1
18	1	2025-01-24	1
19	2	2025-02-03	1
20	2	2025-02-04	1
21	2	2025-02-05	1
1	1	2024-11-25	2
3	1	2024-11-26	2
12	1	2025-01-07	2
23	1	2024-11-21	1
24	1	2024-11-22	1
25	1	2024-11-22	1
26	1	2025-02-03	2
27	1	2024-11-29	1
28	1	2024-11-30	1
22	1	2024-11-21	2
29	2	2024-11-25	1
\.


--
-- Data for Name: student; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.student (user_id, contact_id, student_number, university_id, enrollment_end) FROM stdin;
3	3	2024001	1	2025-09-30
\.


--
-- Data for Name: university; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.university (university_id, university_name, contact_id) FROM stdin;
1	FH Burgenland	1
2	TU Graz	2
3	University of Vienna	3
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public."user" (user_id, role_id, provider_id, verification, verification_date, email, oauth_token, first_name, last_name) FROM stdin;
1	2	1	t	2024-11-20	oejab_eisenstadt	\N	Franz	Hilber
2	2	2	t	2024-11-20	hotela	\N	Igraine	OhneZahn
3	3	\N	t	2024-11-20	tbaier	\N	Tatjana	Baier
\.


--
-- Name: accommodation_provider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.accommodation_provider_id_seq', 2, true);


--
-- Name: booking_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.booking_booking_id_seq', 2, true);


--
-- Name: booking_state_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.booking_state_state_id_seq', 5, true);


--
-- Name: contact_kontakt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.contact_kontakt_id_seq', 3, true);


--
-- Name: role_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.role_role_id_seq', 3, true);


--
-- Name: room_room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.room_room_id_seq', 29, true);


--
-- Name: university_university_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.university_university_id_seq', 1, false);


--
-- Name: user_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.user_user_id_seq', 3, true);


--
-- Name: accommodation accommodation_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.accommodation
    ADD CONSTRAINT accommodation_pkey PRIMARY KEY (provider_id);


--
-- Name: booking booking_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_pkey PRIMARY KEY (booking_id);


--
-- Name: booking_state booking_state_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.booking_state
    ADD CONSTRAINT booking_state_pkey PRIMARY KEY (state_id);


--
-- Name: contact contact_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_pkey PRIMARY KEY (contact_id);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (role_id);


--
-- Name: room room_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT room_pkey PRIMARY KEY (room_id);


--
-- Name: student student_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_pkey PRIMARY KEY (user_id);


--
-- Name: university university_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.university
    ADD CONSTRAINT university_pkey PRIMARY KEY (university_id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);


--
-- Name: accommodation accommodation_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.accommodation
    ADD CONSTRAINT accommodation_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contact(contact_id);


--
-- Name: booking booking_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.room(room_id);


--
-- Name: booking booking_state_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_state_id_fkey FOREIGN KEY (state_id) REFERENCES public.booking_state(state_id);


--
-- Name: booking booking_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(user_id);


--
-- Name: room room_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT room_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.accommodation(provider_id);


--
-- Name: room room_state_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT room_state_id_fkey FOREIGN KEY (state_id) REFERENCES public.booking_state(state_id);


--
-- Name: student student_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contact(contact_id);


--
-- Name: student student_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.university(university_id);


--
-- Name: student student_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(user_id);


--
-- Name: university university_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public.university
    ADD CONSTRAINT university_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contact(contact_id);


--
-- Name: user user_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.accommodation(provider_id);


--
-- Name: user user_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(role_id);


--
-- PostgreSQL database dump complete
--
