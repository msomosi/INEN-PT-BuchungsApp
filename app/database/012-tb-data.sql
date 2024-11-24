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
-- Data for Name: tbl_buchung; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.tbl_buchung (buchung_id, user_id, zimmer_id) FROM stdin;
1	3	6
3	3	1
4	3	3
5	3	12
6	3	26
7	3	22
\.


--
-- Data for Name: tbl_user; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.tbl_user (user_id, role_id, verification, verification_date, username, password) FROM stdin;
1	2	t	2024-11-20	oejab_eisenstadt    	oejab_eisenstadt
2	2	t	2024-11-20	hotela              	hotela
3	3	t	2024-11-20	tbaier              	tbaier
\.


--
-- Data for Name: tbl_user_details; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.tbl_user_details (user_id, "CompanyName", "Firstname", "Lastname", "Matrikelnummer", "University", "Inskription_end", "Adresse", "Plz", "Location", notice, email, phone, "Koordinaten", "Parking", parking_pay) FROM stdin;
1	OEJAB Eisenstadt                                  	Franz               	Hilber              	1	                                                  	1	Campus 2                                                                                            	7000	Eisenstadt                                        	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                	oejab@user1.at                                                                                      	0126485682               	\N	t	t
2	Hotel A                                           	Igraine             	OhneZahn            	2	                                                  	2	Rechbauerstraße 12                                                                                  	8010	Graz                                              	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                	test@test.at                                                                                        	06642158713365           	\N	f	f
3	                                                  	Tatjana             	Baier               	153003	FH Burgenland                                     	1986	Kalvarienbergstraße 16a                                                                             	8020	Graz                                              	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                	                                                                                                    	                         	                                                                                                                                                                                                        	t	f
\.


--
-- Data for Name: tbl_zimmer; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY public.tbl_zimmer (zimmer_id, user_id, date, state_id) FROM stdin;
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
-- Name: tbl_buchung_buchung_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_buchung_buchung_id_seq', 7, true);


--
-- Name: tbl_buchung_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_buchung_user_id_seq', 1, false);


--
-- Name: tbl_buchung_zimmer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_buchung_zimmer_id_seq', 1, false);


--
-- Name: tbl_user_details_Inskription_end_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public."tbl_user_details_Inskription_end_seq"', 2, true);


--
-- Name: tbl_user_details_Matrikelnummer_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public."tbl_user_details_Matrikelnummer_seq"', 2, true);


--
-- Name: tbl_user_details_Plz_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public."tbl_user_details_Plz_seq"', 1, false);


--
-- Name: tbl_user_details_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_user_details_user_id_seq', 3, true);


--
-- Name: tbl_user_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_user_role_id_seq', 1, false);


--
-- Name: tbl_user_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_user_user_id_seq', 2, true);


--
-- Name: tbl_zimmer_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_zimmer_state_id_seq', 8, true);


--
-- Name: tbl_zimmer_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_zimmer_user_id_seq', 1, false);


--
-- Name: tbl_zimmer_zimmer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('public.tbl_zimmer_zimmer_id_seq', 29, true);


--
-- PostgreSQL database dump complete
--
