#ifndef CORE_TOOL_H_
#define CORE_TOOL_H_
#if defined(SHAREDLIB_LIBRARY)
    #define SHAREDLIB_EXPORT Q_DECL_EXPORT
#else
    #define SHAREDLIB_EXPORT Q_DECL_IMPORT
#endif
#endif

