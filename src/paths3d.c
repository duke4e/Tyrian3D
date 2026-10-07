/*
 * Tyrian3D: where the 3D view's resources are. See paths3d.h.
 */
#include "paths3d.h"

#include <SDL3/SDL.h>

const char *tyr3d_resource_dir(const char *env, const char *built, const char *name, char *buffer, size_t size)
{
	const char *value = env != NULL ? SDL_getenv(env) : NULL;
	if (value != NULL)
	{
		SDL_strlcpy(buffer, value, size);
		return buffer;
	}

	SDL_PathInfo info;
	if (built != NULL && SDL_GetPathInfo(built, &info) && info.type == SDL_PATHTYPE_DIRECTORY)
	{
		SDL_strlcpy(buffer, built, size);
		return buffer;
	}

	const char *base = SDL_GetBasePath();
	SDL_snprintf(buffer, size, "%s%s", base != NULL ? base : "", name);
	return buffer;
}
