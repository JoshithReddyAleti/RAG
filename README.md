# RAG

I am creating a chat bot with RAG features
i will list some features build it based on the req's
1)The RAG should basically input a file and exact output from it and store it in chunks, from storing it from chuks, if the user asks for any information, it should retreive the info from the chuks and embeeding files. It should work for all text inputs or even shuld work for images when extracting the data.
2)Not just giving the output from it but it should also give cititation from where dod it take from like what file, what page number and what line with as much as accuracy
3) Example, if i input a file like pdf or txt of user manual of a car of 200 pages, it should store all the info and make it as chunks by embeeding it, and later when i ask a question like : How to fix spark plugs?
it should search all the pages info and give me response, and finally show where did it get the info from! like page number and line with most accuracy
4)Its just implementing RAG, it should give responses only based on the pdf if users ask info from pdfs, and if user ask info in general, then it should use ai to give reponses but even that case it should give citiations

5)I dont need any UI for it but need the implementation of logic, i can ask questions in terminal for now and when everything is working then i will generate an API to keep it in alrweady exosting UI.

6) I am doing it in secure sever fiserv, so i will havng very limited access to ai and all. I already have files created in my computer. I will say the names of the files from their give what enhancements we need to acquire what i want?

files i have,

__pycache__
chunks -> testai.json, testpdf.json, xd_pdf_with_images.json
output->chroma_db
output->TestAI.md, testpdf.md, xd_pdf_with_images.md
upload-> testAI.txt, testpdf.pdf, xd_pdf_with_images.pdf
.env
ai.py
requirements.txt
XD_RAG.py
