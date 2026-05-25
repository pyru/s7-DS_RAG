import type { PdfBook } from '../types';

export const PDFS: PdfBook[] = [
  // ── Python & Data Science ─────────────────────────────────────────
  { id:'pdf-001', title:'Python Data Science Handbook',                             author:'Jake VanderPlas',             year:'2016', category:'Python & Data Science' },
  { id:'pdf-002', title:'Python for Data Analysis',                                 author:'Wes McKinney',                year:'2022', category:'Python & Data Science' },
  { id:'pdf-003', title:'Python Crash Course',                                      author:'Eric Matthes',                year:'2023', category:'Python & Data Science' },
  { id:'pdf-004', title:'Python for Data Science: A Hands-On Introduction',         author:'Yuli Vasiliev',               year:'2022', category:'Python & Data Science' },
  { id:'pdf-005', title:'Python All-in-One For Dummies',                            author:'Shovic & Simpson',            year:'2021', category:'Python & Data Science' },
  { id:'pdf-006', title:'Python Machine Learning By Example',                       author:'Yuxi Liu',                    year:'2020', category:'Python & Data Science' },
  { id:'pdf-007', title:'Python Programming: The Complete Guide',                   author:'Nicholas Ayden',              year:'2019', category:'Python & Data Science' },
  { id:'pdf-008', title:'Data Science at the Command Line',                         author:'Jeroen Janssens',             year:'2014', category:'Python & Data Science' },

  // ── Machine Learning — Core ───────────────────────────────────────
  { id:'pdf-009', title:'Hands-On Machine Learning with Scikit-Learn, Keras & TF',  author:'Aurélien Géron',              year:'2023', category:'Machine Learning' },
  { id:'pdf-010', title:'The Hundred-Page Machine Learning Book',                   author:'Andriy Burkov',               year:'2019', category:'Machine Learning' },
  { id:'pdf-011', title:'Machine Learning for Absolute Beginners',                  author:'Oliver Theobald',             year:'2020', category:'Machine Learning' },
  { id:'pdf-012', title:'Machine Learning Yearning',                                author:'Andrew Ng',                   year:'2018', category:'Machine Learning' },
  { id:'pdf-013', title:'Introduction to Machine Learning with Python',             author:'Müller & Guido',              year:'2016', category:'Machine Learning' },
  { id:'pdf-014', title:'Machine Learning Design Patterns',                         author:'Lakshmanan, Robinson, Munn',  year:'2020', category:'Machine Learning' },
  { id:'pdf-015', title:'The StatQuest Illustrated Guide to Machine Learning',      author:'Josh Starmer',                year:'2022', category:'Machine Learning' },
  { id:'pdf-016', title:'Machine Learning Algorithms From Scratch',                 author:'Jason Brownlee',              year:'2018', category:'Machine Learning' },

  // ── Deep Learning ─────────────────────────────────────────────────
  { id:'pdf-017', title:'Deep Learning',                                            author:'Goodfellow, Bengio, Courville',year:'2016', category:'Deep Learning' },
  { id:'pdf-018', title:'Deep Learning Pipeline with TensorFlow',                   author:'El-Amir & Hamdy',             year:'2020', category:'Deep Learning' },
  { id:'pdf-019', title:'Deep Learning with Python',                                author:'Jason Brownlee',              year:'2019', category:'Deep Learning' },

  // ── Statistics & Mathematics ──────────────────────────────────────
  { id:'pdf-020', title:'Think Stats: Probability and Statistics for Programmers',  author:'Allen B. Downey',             year:'2011', category:'Statistics & Math' },
  { id:'pdf-021', title:'Mathematics for Machine Learning',                         author:'Deisenroth, Faisal, Ong',     year:'2021', category:'Statistics & Math' },
  { id:'pdf-022', title:'Introductory Business Statistics',                         author:'OpenStax',                    year:'2021', category:'Statistics & Math' },
  { id:'pdf-023', title:'Foundations of Probabilistic Programming',                 author:'Barthe, Katoen, Silva',       year:'2021', category:'Statistics & Math' },
  { id:'pdf-024', title:'Introduction to Statistical Relational Learning',          author:'Getoor & Taskar',             year:'2007', category:'Statistics & Math' },
  { id:'pdf-025', title:'Modeling and Simulation in Python',                        author:'Allen B. Downey',             year:'2023', category:'Statistics & Math' },

  // ── Systems & Engineering ─────────────────────────────────────────
  { id:'pdf-026', title:'Designing Machine Learning Systems',                       author:'Chip Huyen',                  year:'2022', category:'Systems & Engineering' },
  { id:'pdf-027', title:'Designing Data-Intensive Applications',                    author:'Martin Kleppmann',            year:'2018', category:'Systems & Engineering' },
  { id:'pdf-028', title:'Fundamentals of Data Engineering',                         author:'Reis & Housley',              year:'2022', category:'Systems & Engineering' },
  { id:'pdf-029', title:'System Design Interview',                                  author:'Alex Xu',                     year:'2020', category:'Systems & Engineering' },
  { id:'pdf-030', title:'Machine Learning Design Interview',                        author:'Khang Pham',                  year:'2022', category:'Systems & Engineering' },

  // ── Algorithms & Coding ───────────────────────────────────────────
  { id:'pdf-031', title:'Grokking Algorithms',                                      author:'Aditya Bhargava',             year:'2016', category:'Algorithms & Coding' },
  { id:'pdf-032', title:'Data Structures and Algorithm Analysis in Java',           author:'Mark Allen Weiss',            year:'2012', category:'Algorithms & Coding' },
  { id:'pdf-033', title:'Cracking the Coding Interview',                            author:'Gayle Laakmann McDowell',     year:'2015', category:'Algorithms & Coding' },
  { id:'pdf-034', title:'The Recursive Book of Recursion',                          author:'Al Sweigart',                 year:'2022', category:'Algorithms & Coding' },
  { id:'pdf-035', title:'Programming Interview Problems: Dynamic Programming',      author:'Leonardo Rossi',              year:'2020', category:'Algorithms & Coding' },
  { id:'pdf-036', title:'Data Science from Scratch',                                author:'Steven Cooper',               year:'2019', category:'Algorithms & Coding' },

  // ── Interview Preparation ─────────────────────────────────────────
  { id:'pdf-037', title:'DSI ACE PREP — Data Science Interview Handbook',           author:'Data Science Interview Books',year:'2021', category:'Interview Prep' },
  { id:'pdf-038', title:'Data Science & ML Interview Questions Using Python',       author:'Vishwanathan Narayanan',       year:'2021', category:'Interview Prep' },
  { id:'pdf-039', title:'500 Most Important Data Science Interview Q&A',            author:'Vamsee Puligadda',            year:'2018', category:'Interview Prep' },
  { id:'pdf-040', title:'120 Real Data Science Interview Questions',                author:'Shan, Song, Wang, Chen',      year:'2015', category:'Interview Prep' },
  { id:'pdf-041', title:'Imbalanced Classification with Python',                    author:'Jason Brownlee',              year:'2020', category:'Interview Prep' },

  // ── Visualization & BI ────────────────────────────────────────────
  { id:'pdf-042', title:'Data Storytelling and Visualization with Tableau',         author:'Joshi & Mahalle',             year:'2022', category:'Visualization & BI' },
  { id:'pdf-043', title:'The Tableau Workshop',                                     author:'Gupta, Pinto et al.',         year:'2020', category:'Visualization & BI' },
  { id:'pdf-044', title:'Microsoft Power BI For Dummies',                           author:'Jack A. Hyman',               year:'2022', category:'Visualization & BI' },
  { id:'pdf-045', title:'Excel Data Analysis For Dummies',                          author:'Paul McFedries',              year:'2022', category:'Visualization & BI' },
  { id:'pdf-046', title:'Excel All-in-One',                                         author:'McFedries & Harvey',          year:'2022', category:'Visualization & BI' },

  // ── Other ─────────────────────────────────────────────────────────
  { id:'pdf-047', title:'Chaos: Making a New Science',                              author:'James Gleick',                year:'1987', category:'Other' },
  { id:'pdf-048', title:'Modeling and Simulation in Python (2nd Ed.)',              author:'Allen B. Downey',             year:'2023', category:'Other' },
  { id:'pdf-049', title:'Linux For Dummies',                                        author:'Richard Blum',                year:'2020', category:'Other' },
];
