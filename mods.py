#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mods.py — ALL course content for C++ Master.

Tranche 1 (complete): 11 core modules · 61 lessons · C++98 → C++23,
plus the base flashcard deck (40), cheat sheet (10 categories) and
glossary (47 terms).

CONTINUATION: append the v2.0 modules (Memory Model, Advanced Templates,
Design Patterns, Best Practices, Interview Prep, Guided Projects) and
extension Parts 1–8 to the marked slot near the bottom — the helpers and
_add_lesson() are already provided there.
"""

# ============================================================================
#  CONTENT HELPERS
# ============================================================================
def T(x):            return {"t": "text", "x": x}
def HD(x):           return {"t": "h", "x": x}
def C(x, out=None):  return {"t": "code", "x": x, "out": out}
def N(x):            return {"t": "note", "x": x}
def W(x):            return {"t": "warn", "x": x}
def TB(hd, rows):    return {"t": "table", "hd": hd, "rows": rows}
def Q(q, ch, a, why=""): return {"q": q, "ch": ch, "a": a, "why": why}
def LS(title, std, blocks, quiz=None):
    return {"title": title, "std": std, "blocks": blocks, "quiz": quiz or []}
def MOD(title, desc, lessons): return {"title": title, "desc": desc, "lessons": lessons}

# ============================================================================
#  COURSE — 11 modules · 61 lessons
# ============================================================================
MODS = [
MOD("Getting Started", "What C++ is, its standards history, your first program and how compilation works.", [
LS("What is C++? A Tour of the Standards", "Core", [
T("**C++** is a general-purpose, statically-typed, compiled language created by **Bjarne Stroustrup** in 1979 as \"C with Classes\". It combines low-level memory and hardware control with powerful high-level abstractions — its guiding principle is *zero-overhead abstraction*: you don't pay for what you don't use."),
T("It powers operating systems, game engines (Unreal), browsers (Chrome), databases (MySQL, MongoDB), trading systems, embedded devices and more. Since 1998 the language has evolved through ISO standards:"),
TB(["Standard", "Year", "Headline features"], [
 ["C++98/03", "1998/2003", "First ISO standard: classes, templates, STL, strings, streams"],
 ["C++11", "2011", "auto, lambdas, smart pointers, move semantics, threads, range-for"],
 ["C++14", "2014", "Generic lambdas, relaxed constexpr, variable templates"],
 ["C++17", "2017", "structured bindings, if constexpr, optional/variant, filesystem"],
 ["C++20", "2020", "concepts, ranges, coroutines, modules, spaceship operator"],
 ["C++23", "2023", "std::print, std::expected, deducing this, flat containers"]]),
T("This course covers **all of them** — foundations first, then the modern layers each standard added. Lessons are tagged with the standard that introduced each feature."),
], [Q("Which standard introduced lambdas and smart pointers?", ["C++03", "C++11", "C++17", "C++20"], 1,
      "C++11 (2011) was the huge modernization release — 'Modern C++' day one.")]),
LS("Your First Program", "Core", [
T("The traditional starting point — and every piece of it matters:"),
C(r'''#include <iostream>          // preprocessor: pull in the I/O library

int main() {                 // entry point: execution starts here
    std::cout << "Hello, C++!\n";   // write to standard output
    return 0;                // 0 = success (optional in main)
}''', "Hello, C++!"),
HD("Anatomy"),
T("`#include <iostream>` — brings in the input/output stream library. `std::` is the *namespace* of the standard library; `::` is the scope-resolution operator."),
T("`int main()` — every program starts at `main`. It returns an `int` exit code to the operating system."),
T("`std::cout <<` — the *stream insertion operator* chains values to the console. `'\\n'` starts a new line (prefer it over `std::endl` unless you need an explicit flush)."),
C(r'''#include <iostream>

int main() {
    std::cout << "Several" << " values " << 42 << ' ' << 3.14 << '\n';
}''', "Several values 42 3.14"),
N("Every statement ends with a semicolon `;`. Missing it is the #1 beginner compile error."),
], [Q("What is the entry point of every C++ program?", ["start()", "init()", "main()", "begin()"], 2)]),
LS("Compilation & the Toolchain", "Core", [
T("C++ is **ahead-of-time compiled**. Building a program runs four stages:"),
TB(["Stage", "Tool", "What happens"], [
 ["Preprocess", "cpp", "Expand #include / #define, strip comments"],
 ["Compile", "cc1plus etc.", "Translate each .cpp into assembly for your CPU"],
 ["Assemble", "as", "Assembly → object file (.o / .obj) with machine code"],
 ["Link", "ld / link", "Glue object files + libraries into the final executable"]]),
C(r'''# Typical command-line build (g++ / clang++)
g++ -std=c++20 -Wall -Wextra main.cpp -o myprogram
./myprogram'''),
T("Main compilers: **GCC** (g++), **Clang** (clang++) and **Microsoft Visual C++** (MSVC, `cl`). IDEs like Visual Studio, CLion, Qt Creator and VS Code all drive these for you."),
W("Classic first errors: a missing `;`, forgetting `#include <iostream>`, or mismatched braces `{}`. Read the FIRST error the compiler prints — later errors are often cascade noise."),
], [Q("Which stage comes right after preprocessing?", ["Linking", "Compilation", "Assembly", "Loading"], 1,
      "Order: preprocess → compile → assemble → link.")]),
]),

MOD("Core Basics", "Variables, types, initialization, constants, operators, casts, enums and console I/O.", [
LS("Variables & Fundamental Types", "Core", [
T("C++ is **statically typed**: every variable has a type fixed at compile time. A declaration is `type name = value;`."),
TB(["Type", "Typical size", "Holds"], [
 ["bool", "1 byte", "true / false"],
 ["char", "1 byte", "one character (also a small integer)"],
 ["int", "4 bytes", "integers (±2 billion)"],
 ["long long", "8 bytes", "big integers"],
 ["float / double", "4 / 8 bytes", "floating-point numbers"],
 ["unsigned int", "4 bytes", "0 … 4,294,967,295"],
 ["size_t", "8 bytes", "sizes & indices (never negative)"]]),
C(r'''#include <iostream>

int main() {
    int         age   = 30;
    double      price = 9.99;
    char        grade = 'A';
    bool        ok    = true;
    long long   big   = 9000000000LL;
    unsigned    count = 42u;

    std::cout << age << ' ' << price << ' ' << grade << ' '
              << ok << ' ' << big << ' ' << count << '\n';
    std::cout << "bytes: int=" << sizeof(int)
              << " double=" << sizeof(double) << '\n';
}''', "30 9.99 A 1 9000000000 42\nbytes: int=4 double=8"),
W("Sizes are platform-dependent — always ask `sizeof(T)` instead of assuming. `bool` prints as `1`/`0` unless you use `std::boolalpha`."),
N("Unsigned wrap-around is a classic trap: `unsigned u = 0; --u;` yields 4294967295, not -1."),
], [Q("sizeof(int) is…", ["always 4", "at least 2, commonly 4", "always 8", "fixed by C++ at 16"], 1,
      "The standard only guarantees minimums; int is commonly 4 bytes on modern platforms.")]),
LS("Initialization & auto (C++11)", "C++11", [
T("C++ has several initialization forms — and since C++11 you can let the **compiler deduce** types:"),
C(r'''#include <string>
#include <vector>

int main() {
    int a  = 5;     // copy-initialization
    int b (5);      // direct-initialization
    int c {5};      // brace (uniform) initialization — C++11
    // int d {3.9}; // ERROR: braces forbid narrowing conversions!

    auto x = 10;          // deduced: int
    auto y = 3.14;        // deduced: double
    auto z = 1 + 2.0;     // deduced: double
    const auto& ref = x;  // const int& bound to x

    std::vector<int> v{1, 2, 3};   // brace list-init
}'''),
T("**`auto`** (C++11) is not a 'dynamic type' — the type is still fixed at compile time; it just saves you writing `std::vector<std::string>::iterator` by hand. Prefer it for iterators and long template types; be explicit when the type carries meaning."),
N("Brace initialization `{}` is the safest default: it disallows silent narrowing (`int x{3.9}` is an error, `int x = 3.9` silently truncates)."),
], [Q("What does `int x{3.9};` do?", ["Truncates to 3", "Rounds to 4", "Compile error — brace init forbids narrowing", "Undefined behavior"], 2)]),
LS("Constants: const, constexpr, consteval", "C++11", [
T("**`const`** means *read-only after initialization*:"),
C(r'''const double pi = 3.14159;
pi = 3;          // ERROR: cannot modify a const'''),
T("**`constexpr`** (C++11) means *usable in constant expressions* — the compiler may (and for variables, must) evaluate it at compile time. **`consteval`** (C++20) forces compile-time evaluation of functions."),
C(r'''#include <iostream>

constexpr int square(int x) { return x * x; }   // C++11

int main() {
    constexpr int side = 7;                // compile-time constant
    int arr[square(side)];                 // OK: size known at compile time
    static_assert(sizeof(arr) == 49 * sizeof(int));

    int user = 5;                          // a runtime value
    std::cout << square(user) << '\n';     // still fine: runs at runtime
}''', "25"),
N("Rule of thumb: `constexpr` for anything computable at compile time (faster binaries, compile-time errors instead of runtime bugs). `const` for read-only runtime data."),
], [Q("Which keyword guarantees a *variable* is a compile-time constant?", ["const", "constexpr", "static", "inline"], 1)]),
LS("Operators & Expressions", "Core", [
TB(["Category", "Operators"], [
 ["Arithmetic", "+  -  *  /  %  ++  --"],
 ["Relational", "==  !=  <  >  <=  >=  <=>  (C++20 three-way)"],
 ["Logical", "&&  ||  !"],
 ["Bitwise", "&  |  ^  ~  <<  >>"],
 ["Assignment", "=  +=  -=  *=  /=  %=  &=  |=  ^=  <<=  >>=  (C++20 ==/!= rewritten)"],
 ["Other", "?: (ternary)  ,  sizeof  ::"]]),
C(r'''#include <iostream>

int main() {
    int a = 17, b = 5;
    std::cout << a / b   << '\n';   // 3   — integer division truncates!
    std::cout << a % b   << '\n';   // 2   — remainder
    std::cout << a / 5.0 << '\n';   // 3.4 — floating-point division

    bool hot = true, sunny = false;
    std::cout << (hot && sunny) << (hot || sunny) << (!hot) << '\n';

    int flags = 0b1100;             // binary literal (C++14)
    std::cout << (flags & 0b1010) << ' ' << (flags | 0b0011) << ' '
              << (flags ^ 0b0110) << ' ' << (flags << 1) << '\n';

    int max = (a > b) ? a : b;      // ternary / conditional operator
    std::cout << "max=" << max << '\n';
}''', "3\n2\n3.4\n010\n8 15 10 24\nmax=17"),
W("`&&` and `||` *short-circuit* (the right side may not run). Integer division `17 / 5` is `3`, not `3.4` — a top bug source. When in doubt, use parentheses."),
], [Q("What does `17 / 5` evaluate to with int operands?", ["3.4", "3", "4", "2"], 1,
      "Integer division truncates toward zero. Cast one operand to double for 3.4.")]),
LS("Explicit Type Conversion (Casting)", "Core", [
T("C++ converts types implicitly (e.g. `int` → `double`), but silent narrowing (`double` → `int`) loses data. For explicit conversions, use the **C++ named casts** instead of C-style `(int)x`:"),
TB(["Cast", "Use for"], [
 ["static_cast", "Sane, checked-at-compile-time conversions (numeric, up-casts)"],
 ["dynamic_cast", "Safe downcasts in class hierarchies (needs virtual functions)"],
 ["const_cast", "Add/remove const (rare, dangerous)"],
 ["reinterpret_cast", "Raw bit reinterpretation — last resort, platform-specific"]]),
C(r'''#include <iostream>

class Base { public: virtual ~Base() = default; };
class Derived : public Base { public: void hello() { std::cout << "Derived!\n"; } };

int main() {
    double d = 3.99;
    std::cout << static_cast<int>(d) << '\n';        // 3 — explicit truncation

    Base* b = new Derived();
    if (auto* der = dynamic_cast<Derived*>(b))       // safe downcast
        der->hello();
    delete b;

    long addr = reinterpret_cast<long>(&d);          // bits as integer (avoid!)
    std::cout << (addr != 0) << '\n';
}''', "3\nDerived!\n1"),
N("Modern guideline: design so you rarely need casts. static_cast covers 95% of real needs; reach for the others only with a concrete reason."),
], [Q("Safest cast for a numeric conversion like double→int?", ["reinterpret_cast", "C-style (int)x", "static_cast", "const_cast"], 2)]),
LS("Enums", "C++11", [
T("Enums name integral constants. C++11 added **scoped enums** (`enum class`) which are strongly typed and don't leak their names:"),
C(r'''#include <iostream>

enum Color { Red, Green, Blue };            // unscoped (C++98)
enum class Fruit : char { Apple, Pear };    // scoped (C++11), underlying type char

int main() {
    Color c = Green;
    int n = c;                    // OK: unscoped enums implicitly convert to int
    std::cout << c << ' ' << n << '\n';

    Fruit f = Fruit::Pear;        // must qualify the name
    // int bad = f;               // ERROR: no implicit conversion — a feature!
    std::cout << static_cast<int>(f) << '\n';

    switch (c) {
        case Red:   std::cout << "red\n";   break;
        case Green: std::cout << "green\n"; break;
        default:    std::cout << "blue\n";  break;
    }
}''', "1 1\n1\ngreen"),
N("Prefer `enum class` in modern code: no namespace pollution, no accidental comparisons with integers."),
], [Q("Key advantage of `enum class` over plain `enum`?", ["It is faster", "Scoped names + no implicit int conversion", "Uses less memory", "Auto-serializes"], 1)]),
LS("Console I/O & Stream Manipulators", "Core", [
C(r'''#include <iostream>
#include <iomanip>
#include <string>

int main() {
    std::string name;
    int age;
    std::cout << "Name: ";
    std::getline(std::cin, name);       // whole line, including spaces
    std::cout << "Age: ";
    std::cin >> age;                    // >> skips whitespace, stops at spaces

    std::cout << "Hi " << name << ", next year you'll be " << age + 1 << '\n';
    std::cout << std::fixed << std::setprecision(2) << 3.14159 << '\n';
    std::cout << std::setw(6) << 42 << "|\n";       // width-aligned
}''', "Name: Ada Lovelace\nAge: 36\nHi Ada Lovelace, next year you'll be 37\n3.14\n    42|"),
T("Useful manipulators from `<iomanip>` / `<ios>`: `std::fixed`, `std::setprecision`, `std::setw`, `std::boolalpha` (print `true`/`false`), `std::hex` / `std::oct`, `std::left` / `std::right`."),
W("`std::cin >> x;` leaves the trailing newline in the buffer — mixing it with `getline` can skip a line. Watch for that classic gotcha."),
], [Q("How do you read a full line containing spaces?", ["std::cin >> s", "std::getline(std::cin, s)", "std::cin.getline(s)", "read(s)"], 1)]),
]),

MOD("Control Flow", "Decisions, loops and iteration — including range-based for from C++11.", [
LS("Decisions: if / else / switch", "C++17", [
C(r'''#include <iostream>
#include <string>

std::string classify(int score) {
    if (score >= 90)      return "excellent";
    else if (score >= 70) return "good";
    else if (score >= 50) return "pass";
    else                  return "fail";
}

int main() {
    // C++17: if with initializer — variable scoped to the if/else
    if (int s = 84; classify(s) != "fail")
        std::cout << s << " -> " << classify(s) << '\n';

    int key = 2;
    switch (key) {
        case 1:  std::cout << "one\n";   break;   // break is essential!
        case 2:  std::cout << "two\n";   break;
        case 3:  std::cout << "three\n"; break;
        default: std::cout << "many\n";  break;
    }

    // C++17: constexpr if — the false branch is discarded at compile time
    if constexpr (sizeof(int) == 4)
        std::cout << "int is 4 bytes here\n";
}''', "84 -> good\ntwo\nint is 4 bytes here"),
N("`switch` works on integral types and enums. Forgetting `break` causes *fall-through* into the next case — occasionally useful, usually a bug. Some compilers warn with `-Wimplicit-fallthrough`."),
], [Q("Forgetting `break` inside a switch case causes…", ["A compile error", "Fall-through into the next case", "A runtime crash", "default to always run"], 1)]),
LS("Loops: for, while, do-while", "Core", [
C(r'''#include <iostream>

int main() {
    for (int i = 0; i < 3; ++i)        // init; condition; step
        std::cout << i << ' ';
    std::cout << '\n';

    int n = 8;
    while (n > 1) {                    // check first — may run 0 times
        std::cout << n << ' ';
        n /= 2;
    }
    std::cout << '\n';

    int attempts = 0;
    do { ++attempts; } while (attempts < 0);   // body runs at least once
    std::cout << attempts << '\n';

    for (int i = 0; i < 5; ++i) {
        if (i == 3) break;             // leave the loop entirely
        if (i == 1) continue;          // skip to next iteration
        std::cout << i << ' ';
    }
}''', "0 1 2\n8 4 2\n1\n0 2"),
N("Prefer `++i` over `i++` by habit (never slower, sometimes faster). Avoid `goto` — structured loops and functions express everything you need."),
], [Q("A do-while loop executes its body…", ["Zero or more times", "At least once", "Exactly once", "Until break is hit"], 1)]),
LS("Range-based for (C++11)", "C++11", [
T("The cleanest way to visit every element of any range — containers, arrays, strings, initializer lists:"),
C(r'''#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> langs{"C", "C++98", "C++11", "C++20"};

    for (const std::string& l : langs)   // read-only: bind by const reference
        std::cout << l << ' ';
    std::cout << '\n';

    for (auto& l : langs) l += "!";      // mutate through a reference
    for (auto l : langs) std::cout << l << ' ';   // copies each element
    std::cout << '\n';

    // C++20: initializer in the range-for itself
    for (auto v = std::vector{5, 3, 1}; const int& e : v)
        std::cout << e << ' ';
}''', "C C++98 C++11 C++20\nC! C++98! C++11! C++20!\n5 3 1"),
W("`for (auto l : langs)` copies every element. For big types use `const auto&` to read, or `auto&` to modify. Temporary containers in the loop header live for the whole loop — safe."),
], [Q("`for (auto x : bigVector)` …", ["binds each element by reference", "copies each element", "moves each element", "does not compile"], 1,
      "By-value range-for copies every element; use const auto& to read cheaply.")]),
]),
])


# ... (remaining core modules go here, in MODS, above this line) ...

# ============================================================================
#  CONTINUATION SLOT
#  Append here: (a) the six v2.0 modules, (b) extension Parts 1–8.
#  Everything below is already wired for them.
# ============================================================================
def _add_lesson(module_title, lesson):
    for _m in MODS:
        if _m["title"] == module_title:
            _m["lessons"].append(lesson); return
    MODS.append(MOD(module_title, "", [lesson]))

def _extend(mods):
    MODS.extend(mods)

# _extend([ MOD("Memory Model & Low-Level", "…", [ … ]) , … ])   # v2.0
# _add_lesson("Functions", LS("Lambdas in Depth…"))              # Parts 1–8

TOTAL_LESSONS = sum(len(m["lessons"]) for m in MODS)

# ============================================================================
#  FLASHCARDS (40) · CHEAT SHEET (10 categories) · GLOSSARY (47)
# ============================================================================
FLASHCARDS = [
 ("Which standard added lambdas?", "C++11"),
 ("Which standard added concepts & ranges?", "C++20"),
 ("Which standard added structured bindings?", "C++17"),
 ("std::string::npos — what is it?", "The 'not found' result of find(); largest size_t, not -1"),
 ("Complexity of map::find?", "O(log n) — red-black tree"),
 ("Complexity of unordered_map::find?", "O(1) average, O(n) worst"),
 ("vector::push_back complexity?", "Amortized O(1) — occasional reallocation"),
 ("Which smart pointer by default?", "std::unique_ptr — sole owner, zero overhead"),
 ("Why virtual destructors?", "Deleting Derived via Base* without one is UB"),
 ("Rule of 0?", "Compose from value types; define no copy/move/dtor yourself"),
 ("Rule of 5?", "dtor, copy ctor, copy assign, move ctor, move assign — all or none"),
 ("What does std::move do?", "Casts to rvalue so a move ctor/assign is selected; moves nothing itself"),
 ("const int* vs int* const?", "Pointer to const int vs const pointer to int (read right-to-left)"),
 ("What is RAII?", "Acquire in constructor, release in destructor — automatic cleanup"),
 ("Purpose of noexcept on move ctor?", "vector uses moves during realloc only if they can't throw"),
 ("enum class advantage?", "Scoped names, no implicit conversion to int"),
 ("Brace init {} superpower?", "Forbids narrowing conversions"),
 ("auto& vs auto in range-for?", "auto& binds a reference (no copy); auto copies each element"),
 ("emplace_back vs push_back?", "emplace constructs in place from args; push_back copies/moves"),
 ("map[] vs map.at()?", "[] inserts default if missing; at() throws out_of_range"),
 ("What is SFINAE?", "Substitution Failure Is Not An Error — invalid template substitution removes the overload"),
 ("CRTP gives…", "Static polymorphism — base calls derived, no vtable overhead"),
 ("Perfect forwarding needs…", "T&& universal reference + std::forward<T>"),
 ("What is UB?", "Undefined behavior: signed overflow, OOB, use-after-free, races…"),
 ("Purpose of std::span?", "Non-owning view of contiguous data carrying pointer + size (C++20)"),
 ("string_view danger?", "Non-owning — must not outlive the string it views"),
 ("if constexpr does what?", "Discards the false branch at compile time per instantiation"),
 ("constexpr vs consteval?", "constexpr may run at compile time; consteval must"),
 ("std::optional is for…", "A value that may be absent — replaces sentinel codes"),
 ("std::variant is for…", "A safe tagged union — exactly one of several types"),
 ("What is a data race?", "Two threads access the same memory, ≥1 writes, unsynchronized = UB"),
 ("condition_variable::wait needs…", "A predicate (or loop) — handles spurious wakeups"),
 ("jthread vs thread?", "jthread auto-joins and supports stop_token (C++20)"),
 ("What does std::forward preserve?", "The argument's value category (lvalue stays lvalue, rvalue stays rvalue)"),
 ("erase-remove idiom…", "v.erase(std::remove(v.begin(), v.end(), x), v.end()) — or std::erase in C++20"),
 ("operator<=> (spaceship)?", "Generates all six comparisons; = default if members compare"),
 ("Modules solve…", "Header pollution: explicit export, no macros, faster builds (C++20)"),
 ("std::expected<T,E>?", "Value-or-error return type (C++23) — exceptions-free error handling"),
 ("Half-open range convention?", "[begin, end) — end points past the last element"),
 ("Most cache-friendly container?", "vector/array — contiguous memory"),
]

# FLASHCARDS.extend([ … ])   # extension cards paste here

CHEATSHEET = [
 ("Types & Declarations", [
  ("Core types", "int x = 5;          double d = 3.14;    bool b = true;\nchar c = 'A';       long long L = 9e18LL;\nauto y = x;         // deduced int"),
  ("Const & constexpr", "const double pi = 3.14159;      // runtime read-only\nconstexpr int N = 42;           // compile-time constant\nconsteval int f() { return 1; } // C++20 forced CT"),
  ("auto & braces", "auto it = v.begin();     // deduce long types\nint x{5};                // brace init: no narrowing\nauto v = std::vector{1,2};   // CTAD (C++17)"),
  ("Casts", "static_cast<int>(d)      // numeric / up-cast\ndynamic_cast<Derived*>(b) // checked downcast\nconst_cast<char*>(s)     // rare!\nreinterpret_cast<long>(p)// last resort")]),
 ("Strings", [
  ("Basics", "std::string s = \"hello\";\ns += \" world\";          // append\ns.length();  s[0];  s.substr(1, 3);\ns.find(\"lo\");            // index or npos"),
  ("Conversions", "int n = std::stoi(\"42\");\ndouble d = std::stod(\"3.5\");\nstd::string t = std::to_string(99);"),
  ("string_view (C++17)", "void f(std::string_view sv);   // no-copy param\nf(\"literal\"); f(str); f(str.substr(0,3));"),
  ("C++20/23 extras", "s.starts_with(\"he\");  s.ends_with(\"lo\");\ns.contains(\"ell\");            // C++23\nstd::format(\"{} + {}\", 1, 2);  // C++20")]),
 ("Containers", [
  ("vector", "std::vector<int> v{1,2,3};\nv.push_back(4);  v.pop_back();\nv.size();  v.empty();  v.reserve(100);\nv[i];  v.at(i);  // at throws"),
  ("map / unordered_map", "std::map<K,V> m;  m[k] = v;    // inserts if missing\nm.at(k);  m.find(k);  m.count(k);\nfor (auto& [k, v] : m) …        // C++17"),
  ("set / unordered_set", "std::set<int> s{3,1,2};   // sorted, unique\ns.insert(4); s.count(3);"),
  ("stack / queue / deque", "std::stack<int> st; st.push(1); st.top(); st.pop();\nstd::queue<int> q; q.push(1); q.front(); q.pop();\nstd::deque<int> d; d.push_front(1); d.push_back(2);")]),
 ("Algorithms", [
  ("Sort & search", "std::sort(v.begin(), v.end());\nstd::sort(v.begin(), v.end(), [](auto a, auto b){ return a > b; });\nstd::binary_search(v.begin(), v.end(), x); // needs sorted!"),
  ("Query", "std::find / find_if\nstd::count / count_if\nstd::all_of / any_of / none_of\nstd::max_element / min_element"),
  ("Transform & accumulate", "std::transform(v.begin(), v.end(), out, f);\nint sum = std::accumulate(v.begin(), v.end(), 0);\nstd::copy_if(in, in+n, std::back_inserter(dst), pred);"),
  ("Ranges (C++20)", "for (int x : v | std::views::filter(f)\n               | std::views::transform(g)) …\nstd::ranges::sort(v);")]),
 ("Classes & OOP", [
  ("Class skeleton", "class W {\n    int x_ = 0;                    // default init\npublic:\n    explicit W(int x) : x_(x) {}   // member-init list\n    int get() const { return x_; } // const member\n};"),
  ("Special members", "W(const W&);  W& operator=(const W&);   // copy\nW(W&&) noexcept;  W& operator=(W&&) noexcept; // move\n~W();                                    // destructor\n// Rule of 0: define none if members manage themselves"),
  ("Polymorphism", "class B { public: virtual ~B() = default;\n    virtual void f() const = 0; };      // pure virtual\nstruct D : B { void f() const override {} };"),
  ("Operators", "T operator+(const T&) const;\nbool operator==(const T&) const = default;  // C++20\nauto operator<=>(const T&) const = default; // all 6 ops\nstd::ostream& operator<<(std::ostream&, const T&);")]),
 ("Memory & Smart Pointers", [
  ("Smart pointers", "auto u = std::make_unique<T>(args);  // sole owner\nauto s = std::make_shared<T>(args);  // shared, counted\nstd::weak_ptr<T> w = s;              // observer, breaks cycles\nif (auto l = w.lock()) l->use();"),
  ("Raw new/delete", "T* p = new T{1};   // avoid in modern code\ndelete p;\nT* a = new T[10]; delete[] a;   // match forms!"),
  ("References", "void f(T& x);        // modify caller's\nvoid f(const T& x);  // read-only, no copy"),
  ("Move", "auto b = std::move(a);   // transfer ownership\na;   // valid but unspecified — don't read")]),
 ("Templates", [
  ("Basics", "template <typename T>\nT maxOf(T a, T b) { return a > b ? a : b; }\n\ntemplate <typename T> class Stack { … };"),
  ("Concepts (C++20)", "template <typename T>\nconcept Num = std::integral<T> || std::floating_point<T>;\ntemplate <Num T> T avg(…);\nvoid f(std::integral auto x);"),
  ("Variadics & folds", "template <typename... A>\nauto sum(A... a) { return (a + ... + 0); }"),
  ("if constexpr", "if constexpr (std::is_integral_v<T>) … else …  // CT branching")]),
 ("Concurrency", [
  ("Threads", "std::thread t(f, arg1, arg2);\nt.join();   // or detach()\nstd::jthread jt(f);   // C++20: auto-join"),
  ("Mutexes", "std::mutex m;\n{ std::lock_guard<std::mutex> lk(m); ++shared; }\nstd::scoped_lock lk(m1, m2);   // deadlock-free"),
  ("async & futures", "auto f = std::async(std::launch::async, task);\nauto result = f.get();   // waits + returns"),
  ("Atomics", "std::atomic<int> c{0};\nc++;  c.fetch_add(2);  c.load();")]),
 ("I/O & Filesystem", [
  ("Streams", "std::ofstream out(\"f.txt\");  out << data;\nstd::ifstream in(\"f.txt\");   std::string line;\nwhile (std::getline(in, line)) …\nif (!in) { /* error */ }"),
  ("filesystem (C++17)", "namespace fs = std::filesystem;\nfs::exists(p); fs::create_directories(p);\nfor (auto& e : fs::directory_iterator(\".\")) …\nfs::file_size(p);  fs::remove(p);"),
  ("Formatting", "std::cout << std::fixed << std::setprecision(2) << d;\nstd::cout << std::setw(8) << x;\nstd::println(\"{} items\", n);   // C++23")]),
 ("Modern Highlights", [
  ("C++11", "auto · lambdas · range-for · nullptr\nunique_ptr/shared_ptr · move semantics · threads\nconstexpr · enum class · static_assert"),
  ("C++14/17", "generic lambdas · auto return · binary literals\nstructured bindings [a,b] · if-init · if constexpr\noptional/variant/any · string_view · filesystem"),
  ("C++20/23", "concepts · ranges · coroutines · modules · <=>\nspan · jthread · format · source_location\nprint · expected · deducing this · flat_map")]),
]

# CHEATSHEET.extend([ … ])   # extension categories paste here

GLOSSARY = [
 ("ABI", "Application Binary Interface — binary-level compatibility contract between compiled code."),
 ("Aggregate", "An array or class with no user-provided ctors, no private members — brace-initializable."),
 ("Auto", "Keyword making the compiler deduce a variable's type from its initializer (C++11)."),
 ("CTAD", "Class Template Argument Deduction — deduce template args from ctor args (C++17)."),
 ("Concepts", "Named compile-time requirements on template parameters (C++20)."),
 ("Const-correctness", "Using const pervasively so read-only is enforced by the compiler."),
 ("Constexpr", "Usable in constant expressions; may be evaluated at compile time (C++11)."),
 ("Consteval", "Function that must be evaluated at compile time (C++20)."),
 ("CRTP", "Curiously Recurring Template Pattern: class D derives from Base<D> — static polymorphism."),
 ("Dangling pointer", "A pointer to memory that has been freed — use is undefined behavior."),
 ("Data race", "Unsynchronized concurrent access to memory with at least one write — UB."),
 ("Deduction", "The compiler determining template/parameter types from usage."),
 ("Double dispatch", "Resolving a call on two dynamic types, e.g. via Visitor's accept+visit."),
 ("Emplace", "Construct an element in place inside a container instead of copying/moving it in."),
 ("Exception safety", "Guarantees about state when exceptions propagate (basic/strong/nothrow)."),
 ("Forward declaration", "Declaring a name before its full definition, e.g. class Widget;"),
 ("Half-open range", "[begin, end) — the STL convention where end is one-past-the-last."),
 ("Heap", "Dynamic memory region managed via new/delete or smart pointers."),
 ("Immutable", "Cannot be modified after creation — const/constexpr values."),
 ("Inline namespace", "Namespace whose members are visible in the parent namespace."),
 ("Iteration order", "Order elements are visited: vector = index; map = sorted keys; unordered = hash order."),
 ("Lambda", "Unnamed inline function object with a capture list (C++11)."),
 ("Linkage", "Whether a name can be referred to from other translation units (internal/external)."),
 ("Lvalue / Rvalue", "Identity-having expression vs a (potentially movable) temporary."),
 ("Memory leak", "Allocated memory that is never freed."),
 ("Move semantics", "Transferring resources from a dying object instead of copying (C++11)."),
 ("Mutable", "Member modifiable even inside const member functions."),
 ("Namespace", "Named scope preventing name collisions."),
 ("NRVO", "Named Return Value Optimization — eliding copies when returning a local."),
 ("Overload resolution", "Compiler choosing among same-named functions by argument types."),
 ("Padding", "Invisible bytes inserted for alignment between struct members."),
 ("Polymorphism", "One interface, many behaviors — via virtual functions (runtime) or templates (compile-time)."),
 ("Predicate", "Callable returning bool, used by algorithms like find_if."),
 ("RAII", "Resource Acquisition Is Initialization — lifetime-tied resource management."),
 ("Reference collapsing", "Rules for T&& in deduced contexts: & + && collapse to &."),
 ("SFINAE", "Substitution Failure Is Not An Error — invalid substitutions remove overloads."),
 ("Singleton", "Pattern ensuring exactly one instance with global access."),
 ("Smart pointer", "RAII wrapper owning heap memory: unique_ptr, shared_ptr, weak_ptr."),
 ("Slicing", "Copying a Derived into a Base by value, losing the derived part — avoid."),
 ("Static polymorphism", "Compile-time dispatch via templates/CRTP — no vtable cost."),
 ("Template instantiation", "Compiler generating concrete code from a template for specific arguments."),
 ("Translation unit", "One .cpp file after preprocessing — the unit of compilation."),
 ("UB", "Undefined behavior — code with no defined semantics; optimizers assume it can't happen."),
 ("Universal reference", "T&& with a deduced T — binds to both lvalues and rvalues."),
 ("Value category", "Expression kind: lvalue, xvalue, prvalue — controls what can bind/move where."),
 ("Vtable", "Per-class table of virtual function pointers enabling dynamic dispatch."),
 ("Zero-overhead principle", "You don't pay for abstractions you don't use; used ones cost hand-written code."),
]

# GLOSSARY.extend([ … ])   # extension terms paste here

