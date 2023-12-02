# tagged_titlecaser

This is a demonstration approach to applying a titlecase routine (such as Standard Ebooks titlecase function) to a string which includes HTML tags.

Demo:

```Input: <h2 epub:type="title"><abbr>MR.</abbr> DARCY WAS READING <i epub:type="se:name.publication.book">MOBY-DICK</i></h2>```

```Output: <h2 epub:type="title"><abbr>Mr.</abbr> Darcy Was Reading <i epub:type="se:name.publication.book">Moby-Dick</i></h2>```
