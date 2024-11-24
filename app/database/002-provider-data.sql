--
-- PostgreSQL database dump
--

-- Dumped from database version 14.9 (Debian 14.9-1.pgdg110+1)
-- Dumped by pg_dump version 14.9 (Debian 14.9-1.pgdg110+1)

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

--
-- Data for Name: providers; Type: TABLE DATA; Schema: public; Owner: citizix_user
--

COPY public.providers (id, name, type, address, location, parking_available, parking_paid, always_booked_in) FROM stdin;
1	ÖJAB Eisenstadt	Hotel	Eisenstadt, Österreich	0101000020E61000008A100D41C4883040CA6317563BEA4740	t	f	\N
2	Parkhotel Eisenstadt	Hotel	Eisenstadt, Österreich	0101000020E6100000DF32A7CB628630400C186E0A75EC4740	t	t	\N
3	Gasthof OHR	Hotel	Eisenstadt, Österreich	0101000020E610000000000080A8863040000000607AEB4740	t	f	\N
4	Weingut Lichtscheidl	Hotel	Eisenstadt, Österreich	0101000020E610000000000080BC8C30400000008062ED4740	t	f	2024
5	B&B Hotel Graz	Hotel	Graz, Österreich	0101000020E61000003759FED714DF2E4021109EBFBF834740	t	f	\N
6	Best Western Plus Plaza Hotel Graz	Hotel	Graz, Österreich	0101000020E61000005399BDC7F4E32E40526B50EA81874740	t	f	\N
7	Meininger Hotel Wien	Hotel	Wien, Österreich	0101000020E61000000000002032603040000000000E1C4840	t	f	\N
8	H+ Hotel Wien	Hotel	Wien, Österreich	0101000020E6100000A6BB46263B5B30402F22403C011D4840	t	f	\N
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: citizix_user
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: test_table; Type: TABLE DATA; Schema: public; Owner: citizix_user
--

COPY public.test_table (id, name, created_at) FROM stdin;
1	Test Entry 1	2024-11-19 20:18:03.927378
2	Test Entry 2	2024-11-19 20:18:03.927378
\.


--
-- Name: providers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: citizix_user
--

SELECT pg_catalog.setval('public.providers_id_seq', 8, true);


--
-- Name: test_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: citizix_user
--

SELECT pg_catalog.setval('public.test_table_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--
