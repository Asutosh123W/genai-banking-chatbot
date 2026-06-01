export const apiFetch = async (

  url,
  options = {},
  logout

) => {

  const response =
    await fetch(
      url,
      options
    );

  if (
    response.status === 401
  ) {

    logout();

    throw new Error(
      "Session expired"
    );

  }

  return response;

};