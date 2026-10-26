# graffiti.search

`graffiti.search` is a small Python package that provides a **patch for [collective.solr](https://github.com/collective/collective.solr)** to enable the use of the new placeholder `{raw_value}` in `search_pattern`.  
This allows so-called *exact-ish* phrase searches to be better weighted (*boosted*) in Plone/Solr setups.

---

## Background

By default, `collective.solr` provides the placeholders `{value}` and `{base_value}` for configuring the `search_pattern`.  

However, these are always tokenised by `collective.solr`, which can make exact phrase searches inaccurate.  

With `graffiti.search`, `{raw_value}` is also available, which largely takes over the original search string unedited.

> ⚠ **Caution:** `{raw_value}` should only be used in safe contexts (e.g. within quotation marks) to avoid unexpected Solr syntax errors or incorrect matches.

---

## Installation

The package is part of this repository (`src/graffiti.search`) and listed in `eggs` of `buildout.d/base/sources.cfg`.
In another project add it to the eggs of the instance:

```ini
[instance]
eggs +=
    graffiti.search
```

---

## Activating the patch

Nothing to do: the package applies the patch when Zope loads its ZCML (`<include package=".patches"/>` in `configure.zcml`).
After that, `collective.solr` uses the patched version of `mangleSearchableText`.
The function is a copy of the original, the own parts are marked with `# INTERAKTIV - START` and `# INTERAKTIV - END`.
After an update of `collective.solr` compare it with the original.

---

## Boosting near-exact phrase matches in Solr

One way to achieve this in Solr is by introducing specialized field types like `text_lr` and `text_l`. These fields are designed for "fairly" exact phrase searches, allowing precise control over phrase matching and ranking. The main difference to standard full-text fields lies in how search terms are tokenized and anchored.

### Field types

- **`text_lr` (left-right anchored)**  
  Anchored on both the left **and** right: only if the beginning **and** the end of a phrase match exactly is it considered a hit. This is useful for prioritizing truly exact matches.  
  Example indexing pattern:  
  ```text
  AAAA <SEARCH TERM> ZZZZ
  ````

  (`AAAA` and `ZZZZ` act as artificial anchors for the start and end of the phrase.)

* **`text_l` (left anchored)**  
  Left-anchored only: the beginning of the phrase must match exactly, but the end may vary. Useful when the start of a phrase is crucial, but some fuzziness at the end is acceptable.
  Example indexing pattern:

  ```text
  AAAA <SEARCH TERM>
  ```

### Advantages for ‘fairly’ exact phrase searches

These fields allow **phrase boosting**: hits that match the search phrase exactly or nearly exactly receive a higher score and appear higher in the results. Less precise hits are still found but are ranked lower.
Classic full-text fields often fail here due to stopword removal or token reordering, which can misprioritize matches.

### Why `{raw_value}`?

* `{value}` → tokenized & quoted (good for normal searches, poor for exact phrases)
* `{base_value}` → tokenized without quotes (may lead to inaccurate phrase matching)
* `{raw_value}` → unprocessed, ideal for phrase queries (like `"{raw_value}"`)

Example:

* Search term: `This is a test with C++`
* `{value}` → `[This] [is] [a] [test] [with] [C\+\+]` *(tokenized & quoted, order does not matter)*
* `{base_value}` → `[This] [is] [a] [test] [with] [C++]` *(tokenized, order does not matter)*
* `{raw_value}` → `This is a test with C++` *(unchanged, suitable for phrase queries)*

### Putting it all together

For a fairly exact phrase search, use `{raw_value}` in your Solr search patterns together with `text_lr` and `text_l` fields.

### Test results

Assume two documents:

**Document #1**

* Title: `I am a test`
* Attachment: None
* text\_lr index: `AAAA I am a test ZZZZ`
* text\_l index: `AAAA I am a test`

**Document #2**

* Title: `Totally irrelevant title`
* Attachment: PDF containing: `A test test test test [...]`
* text\_lr index: `AAAA Totally irrelevant title ZZZZ`
* text\_l index: `AAAA Totally irrelevant title`

Search term: `I am a test`

Observations from practical tests:

* Classic searches often remove stopwords, leaving only key tokens (e.g., `test`), which may boost irrelevant documents.
* With `text_lr` and `text_l`, the exact match appears first.
* Some **fuzziness at the end** is allowed: `I am a` also returns matches.
* Partial phrases that do **not** match the beginning (`am a test`) return **no** hits.
* Search queries are **case-insensitive**.
* **Typos** are not handled, but precision remains high.

Want to dig deeper?:
* The Solr Admin Panel and the ‘debugQuery’ option help you understand how a weighting (score) was calculated by explaining it to you step by step.

Further reading:
[Boosting on exact-ish anchored phrase matching in Solr](http://robotlibrarian.billdueber.com/2012/03/boosting-on-exactish-anchored-phrase-matching-in-solr-sst-4/)


---

## Example configuration for ‘exact-ish’ phrase boosting in Solr

Inspired by: [Boosting on exactish anchored phrase matching in Solr](http://robotlibrarian.billdueber.com/2012/03/boosting-on-exactish-anchored-phrase-matching-in-solr-sst-4)

In this repository everything below is already done: the field types and fields are in `solr_config/plone/conf/schema.xml`, the buildout part `solr` (`buildout.d/zeo/solr.cfg`) copies the configuration into the Solr instance.
The search pattern is not part of the code, it lives in the Solr control panel of the site.

### 1. Create new field types in `schema.xml`

```xml
<!-- Text type that anchors on both ends -->
<fieldType name="text_lr" class="solr.TextField" positionIncrementGap="100">
  <analyzer>
    <charFilter class="solr.PatternReplaceCharFilterFactory"
      pattern="^(.*)$" replacement="AAAA $1 ZZZZ" />
    <tokenizer class="solr.ICUTokenizerFactory"/>
    <filter class="solr.ICUFoldingFilterFactory"/>
  </analyzer>
</fieldType>

<!-- Text type that anchors on left end -->
<fieldType name="text_l" class="solr.TextField" positionIncrementGap="100">
  <analyzer>
    <charFilter class="solr.PatternReplaceCharFilterFactory"
      pattern=‘^(.*)$’ replacement="AAAA $1" />
    <tokenizer class="solr.ICUTokenizerFactory"/>
    <filter class="solr.ICUFoldingFilterFactory"/>
  </analyzer>
</fieldType>
```

---

### 2. Create new fields

```xml
<field name="title_exact"        type="text_lr" indexed="true" stored="false" multiValued="false"/>
<field name="title_exact_start"  type="text_l"  indexed="true" stored="false" multiValued="false"/>

<!-- CopyFields -->
<copyField source="Title" dest="title_exact"/>
<copyField source="Title" dest="title_exact_start"/>
```

---

### 3. Include ICU libraries in `solrconfig.xml`

```xml
<!-- ICU LIBS START -->
<lib dir="${solr.install.dir:../../../..}/contrib/analysis-extras/lib" regex=".*\.jar" />
<lib dir="${solr.install.dir:../../../..}/ contrib/analysis-extras/lucene-libs" regex=".*\.jar" />
<lib dir="${solr.install.dir:../../../..}/dist/" regex="solr-analysis-extras-\d.*\.jar" />
<!-- ICU LIBS END -->
```

---

### 4. Configure `search_pattern` in Plone

Go to: **`@@solr-controlpanel`** in Plone and enter, for example:

```
+(title_exact:("{raw_value}")^50 
 OR title_exact_start:("{raw_value}")^25 
 OR Title:{value}^5 
 OR Description:{value}^2 
 OR SearchableText:{value} 
 OR SearchableText:({base_value}) 
 OR searchwords:({base_value})^1000) 
 -showinsearch:False
```

---

### 5. Perform reindexing

1. **Clear Solr Index**
2. Run **Solr Reindex** so that `title_exact` and `title_exact_start` are filled.