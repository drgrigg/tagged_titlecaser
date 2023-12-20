# titlecaser

This is a simple helper function to automatically titlecase chapter headings, etc throughout a Standard Ebooks project. It looks for both `<h1>`, `<h2>` etc as well as attributes such as `epub:type="title"` or `"subtitle"`. It is written in Python.

Note that it shells out to **se titlecase** to do the actual titlecasing, so installation of the SE tools is an essential requirement.

The function correctly handles headings which include tags such as `<abbr>` or semanticated italics such as `<i epub:type="se:name.publication.book">`.
