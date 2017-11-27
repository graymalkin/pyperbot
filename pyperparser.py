# coding=utf-8
import pyparsing as pyp

cmd_arg = pyp.Forward()
t_word = pyp.Regex(r'([^ |\`\'\"\\]|\\\\)+').addParseAction(lambda l, t: ("t_word", l, t[0]))
t_back_index = pyp.Regex(r'\!\:(?P<index>-?\d+)')
t_back_index.addParseAction(lambda s, l, t: ("back_index", l, t))
t_back_range = pyp.Regex(r'\!\:(?P<start>-?\d+)?:(?P<stop>-?\d+)?:?(?P<step>-?\d+)?')
t_back_range.addParseAction(lambda s, l, t: ("back_range", l, t))
t_bracketvar = pyp.nestedExpr('${', '}', content=pyp.CharsNotIn("{}"),
                              ignoreExpr=pyp.quotedString ^ pyp.nestedExpr('{', '}')).addParseAction(
    lambda l, t: ("t_bracketvar", l + 1, t[0][0]))
t_nakedvar = pyp.Suppress('$') + pyp.CharsNotIn(" )([]:+=").addParseAction(lambda l, t: ("t_nakedvar", l, t[0]))
cmd_buffer = pyp.Regex(r"\S*\^(\^+|\d+)?") + pyp.WordEnd()
cmd_buffer.addParseAction(lambda l, t: ("buffer", l, t[0]))
t_tilde = pyp.Suppress('~') + pyp.Regex(r'([^ |\'\"\\]|\\\\)+')
t_tilde.addParseAction(lambda l, t: ("homedir", l, t[0]))
singlequote = pyp.sglQuotedString.addParseAction(lambda l, t: ("singlequote", l, t[0][1:-1]))
doublequote = pyp.dblQuotedString.addParseAction(lambda l, t: ("doublequote", l, t[0][1:-1]))
backquote = pyp.QuotedString(quoteChar='`', escChar='\\').addParseAction(lambda l, t: ("backquote", l, t[0]))
starred = pyp.Suppress(pyp.Literal("*")) + pyp.MatchFirst(
    (t_bracketvar, t_nakedvar, backquote, t_tilde)).addParseAction(lambda l, t: ("starred", l, t[0]))
escaped = pyp.Combine(pyp.Suppress("\\") + pyp.Or(("'", '"', '`'))).addParseAction(lambda l, t: ("escaped", l, t[0]))
cmd_arg << pyp.MatchFirst((t_back_range, t_back_index, starred, cmd_buffer, t_bracketvar, t_nakedvar, singlequote,
                           doublequote, backquote, escaped, t_tilde, t_word))
cmd_name = (pyp.NotAny(pyp.Keyword("alias")) + pyp.Regex(r'([^ |\'\"\\]|\\\\)+')).setParseAction(
    lambda l, t: ("cmd_name", l, t[0]))
command = (cmd_name + pyp.ZeroOrMore(cmd_arg)).addParseAction(lambda l, t: ("command", l, [x for x in t]))
pipeline = (pyp.delimitedList(pyp.Suppress(pyp.ZeroOrMore(pyp.White())) + command, '|')).addParseAction(
    lambda l, t: ("pipeline", l, [x for x in t]))
t_assignment_target = pyp.Regex(r'([^ |\'\"\\]|\\\\)+').addParseAction(
    lambda l, t: ("assignment_target", l, [x for x in t]))
assignment = t_assignment_target + pyp.Suppress('=') + pipeline
assignment.addParseAction(lambda l, t: ("assignment", l, [x for x in t]))
t_alias_word = pyp.Regex(r'([^ |\'\"\\]|\\\\)+').addParseAction(lambda l, t: ("alias_target", l, t[0]))
alias = pyp.Suppress(pyp.Keyword("alias")) + t_alias_word + pyp.Suppress('=') + pipeline
alias.addParseAction(lambda l, t: ("alias", l, [x for x in t]))
inners = pyp.MatchFirst(
    (t_back_range, t_back_index, starred, backquote ^ doublequote, t_bracketvar, t_nakedvar, t_tilde))
total = (alias | assignment | pipeline).addParseAction(lambda l, t: t[0])